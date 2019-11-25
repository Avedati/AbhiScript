from lexer import Token, Tokenizer

"""

 ParsingException
 
 This is a class that inherits from exception. It is used as a custom exception whenever our parser does not like it's input.

"""

class ParsingException(Exception):
	pass

"""

 Parser
 
 This is a class that will take our list of tokens and interpret them as meaningful statements in the Stork language.

"""
class Parser:

	"""
	
	 Parser.__init__(self, tokens)
	 
	 This function is called whenever a new Parser object is created.
	 
	 @param self This instance of the Parser class.
	 @param tokens The array of tokens, passed on from the Tokenizer object.
	
	"""
	def __init__(self, tokens):
		self.tokens = tokens
		self.pos = 0
		self.symbolTable = {}

	"""
	
	 Parser.end(self)
	 
	 Similarly to the same function in the Tokenizer class, this function will return True if this Parser's current position
	 is greater than or equal to the length of it's tokens list.
	 
	 @param self This instance of the Parser class.
	 @return Whether or not our position is outside of the range of the tokens list.
	
	"""
	def end(self):
		return self.pos >= len(self.tokens)

	"""
	
	 Parser.expectType(self, type_)
	 
	 This function is a helper function for the Parser class. It will consume and return the current token,
	 if that token's type matched the specified type. Otherwise, it will raise an exception letting the user know
	 that it expected a different type, and the program will quit.
	 
	 @param self This instance of the Parser class.
	 @param type_ The type which the current token should have.
	 @return The current token (if it's type matched the specified type).
	
	"""
	def expectType(self, type_):
		if not self.end() and self.tokens[self.pos].getType() == type_:
			self.pos += 1
			return self.tokens[self.pos - 1]
		raise ParsingException('Expected type {}, got {}.'.format(type_, self.tokens[self.pos].getType()))
	"""
	
	 Parser.expectLexeme(self, lexeme)
	 
	 This function is a helper function for the Parser class. It will consume and return the current token,
	 if that token's lexeme matched the specified lexeme. Otherwise, it will raise an exception letting the user know
	 that it expected a different lexeme, and the program will quit.
	 
	 @param self This instance of the Parser class.
	 @param lexeme The lexeme which the current token should have.
	 @return The current token (if it's lexeme matched the specified lexeme).
	
	"""
	def expectLexeme(self, lexeme):
		if not self.end() and self.tokens[self.pos].getLexeme() == lexeme:
			self.pos += 1
			return self.tokens[self.pos - 1]
		raise ParsingException('Expected lexeme {}, got {}.'.format(lexeme, self.tokens[self.pos].getLexeme()))

	"""
	
	 Parser.parseCall(self)
	 
	 This function parses a call statement / base. The grammar for a call statement / base is as specified:
	 "call" ( expr... )
	 
	 @param self This instance of the Parser class.
	 @return The result of calling the function.
	
	"""
	def parseCall(self):
		self.expectLexeme('call')
		fnname = self.tokens[self.pos].getLexeme()
		self.pos += 1
		argValues = []

		self.expectLexeme('(')
		while not self.end() and self.tokens[self.pos].getLexeme() != ')':
			argValues.append(self.parseExpr())
		self.expectLexeme(')')

		if self.symbolTable[fnname] is None:
			return
		fn = self.symbolTable[fnname]
		for arg, argValue in zip(fn['args'], argValues):
			self.symbolTable['__' + arg] = argValue
		currentPos = self.pos
		self.pos = fn['statements'][0]
		result = None
		while self.pos < fn['statements'][1] and self.tokens[self.pos] != ')':
			result = self.parseStatement()
		self.expectLexeme(')')
		self.pos = currentPos
		for arg in fn['args']:
			del self.symbolTable['__' + arg]
		return result

	"""
	
	 Parser.parseRawPython(self)
	 
	 This function parses a raw python statement / base. The grammar for a raw python statement / base is as specified:
	 "raw_python_exec" expr | "raw_python_eval" expr
	 
	 @param self This instance of the Parser class.
	 @return The result of evaluating the python string.
	
	"""
	def parseRawPython(self, _type):
		self.expectLexeme('raw_python_' + _type)
		python_src = self.tokens[self.pos].getLexeme()
		self.pos += 1
		new_python_src = ''
		i = 0
		while i < len(python_src):
			if python_src[i] == '\\' and i + 1 < len(python_src):
				new_python_src += '\\' + python_src[i+1]
				i += 1
			elif python_src[i] == '#':
				i += 1
				start = i
				end = -1
				while i < len(python_src) and python_src[i] != '#':
					if python_src[i] == '\\' and i + 1 < len(python_src):
						i += 1
					i += 1
					if python_src[i] == '#':
						end = i
						break
				val = self.symbolTable[python_src[start:end]]
				if type(val) == str:
					new_python_src += '\'' + val + '\''
				else:
					new_python_src += str(val)
				i = end
			else:
				new_python_src += python_src[i]
			i += 1
		if _type == 'exec':
			return exec(new_python_src)
		return eval(new_python_src)

	"""
	
	 Parser.parseArray(self)
	 
	 This function parses an array. The syntax for an array is as follows:
	 "array" ( expr... )
	 
	 @param self This instance of the Parser class.
	 @return An array with the specified values.
	
	"""
	def parseArray(self):
		self.expectLexeme('array')
		self.expectLexeme('(')
		values = []
		while not self.end() and self.tokens[self.pos].getLexeme() != ')':
			values.append(self.parseExpr())
		self.expectLexeme(')')
		return values

	"""
	
	 Parser.parseIf(self)
	 
	 This function parses an if statement. The syntax for an if statement is as follows:
	 "if" expr ( statement... ) | "if" expr ( statement... ) "else" ( statement... )
	 
	 @param self This instance of the Parser class.
	 @return The result of evaluating the if statement (the result of the last statement evaluated).
	
	"""
	def parseIf(self):
		self.expectLexeme('if')
		cond = self.parseExpr()
		if cond:
			self.expectLexeme('(')
			value = None
			while not self.end() and not self.tokens[self.pos].getLexeme() == ')':
				value = self.parseStatement()
			self.expectLexeme(')')
			if self.tokens[self.pos].getLexeme() == 'else':
				self.expectLexeme('else')
				self.expectLexeme('(')
				count = 1
				while not self.end() and count > 0:
					if self.tokens[self.pos].getLexeme() == '(':
						count += 1
					elif self.tokens[self.pos].getLexeme() == ')':
						count -= 1
					self.pos += 1
			return value
		else:
			self.expectLexeme('(')
			count = 1
			while not self.end() and count > 0:
				if self.tokens[self.pos].getLexeme() == '(':
					count += 1
				elif self.tokens[self.pos].getLexeme() == ')':
					count -= 1
				self.pos += 1
			if not self.end() and self.tokens[self.pos].getLexeme() == 'else':
				self.expectLexeme('else')
				self.expectLexeme('(')
				value = None
				while not self.end() and not self.tokens[self.pos].getLexeme() == ')':
					value = self.parseStatement()
				self.expectLexeme(')')
				return value

	"""
	
	 Parser.parseBase(self)
	 
	 This function will parse a base (a number, string, variable, call, array, or raw python statement), and will return it
	 
	 @param self This instance of the Parser class.
	 @return The result of parsing the base. For a number, that would be the float / integer value. For a string, that would be
	         the string. Etc.
	
	"""
	def parseBase(self):
		if self.tokens[self.pos].getType() == 'NUM':
			value = self.tokens[self.pos].getLexeme()
			if '.' in value:
				self.pos += 1
				return float(self.tokens[self.pos - 1].getLexeme())
			self.pos += 1
			return int(self.tokens[self.pos - 1].getLexeme())
		elif self.tokens[self.pos].getType() == 'STR':
			self.pos += 1
			return self.tokens[self.pos - 1].getLexeme()
		elif self.tokens[self.pos].getType() == 'VAR':
			if self.tokens[self.pos].getLexeme() == 'call':
				return self.parseCall()
			elif self.tokens[self.pos].getLexeme() in ['raw_python_eval', 'raw_python_exec']:
				return self.parseRawPython(self.tokens[self.pos].getLexeme()[11:])
			elif self.tokens[self.pos].getLexeme() == 'array':
				return self.parseArray()
			else:
				self.pos += 1
				try:
					return self.symbolTable[self.tokens[self.pos - 1].getLexeme()]
				except KeyError:
					return self.symbolTable['__' + self.tokens[self.pos - 1].getLexeme()]
		
		raise ParsingException('Excepted base, got {}'.format(self.tokens[self.pos].getLexeme()))

	"""
	
	 Parser.parseAtom(self)
	 
	 This function will parse an atom. The syntax for an atom is as follows:
	 base | base [*/%] base
	 
	 @param self This instance of the Parser class.
	 @return The result of the operation, or the original base if no operators were specified.
	
	"""
	def parseAtom(self):
		result = self.parseBase()
		while not self.end() and self.tokens[self.pos].getLexeme() in Tokenizer.ATOM_OPERATORS:
			op = self.expectType('OPR').getLexeme()
			base = self.parseBase()
			if type(base) == str:
				result = eval('result' + str(op) + '\'' + base + '\'')
			else:
				result = eval('result' + str(op) + str(base))
		return result
	
	"""
	
	 Parser.parseExpr(self)
	 
	 This function will parse an expression. The syntax for an expression is as follows:
	 atom | atom [+-] atom
	 
	 @param self This instance of the Parser class.
	 @return The result of the operation, or the original atom if no operators were specified.
	
	"""
	def parseExpr(self):
		result = self.parseAtom()
		while not self.end() and self.tokens[self.pos].getLexeme() in Tokenizer.EXPR_OPERATORS:
			op = self.expectType('OPR').getLexeme()
			atom = self.parseAtom()
			if type(atom) == str:
				result = eval('result' + str(op) + '\'' + atom + '\' if type(result) != int or op != \'+\' else str(result) + atom')
			else:
				result = eval('result' + str(op) + str(atom) + 'if not type(result) in [int,str] or not type(atom) in [int, str] or type(atom) == type(result) or op != \'+\' else str(result) + str(atom)')
		return result

	"""
	
	 Parser.parseAssignment(self)
	 
	 This function will parse an assignment. The syntax for an assignment is as follows:
	 "set" VAR "=" expr
	 
	 @param self This instance of the Parser class.
	 @return The result of the expression that the variable was assigned to.
	
	"""
	def parseAssignment(self):
		self.expectLexeme('set')
		varname = self.tokens[self.pos].getLexeme()
		self.pos += 1
		self.expectLexeme('=')
		value = self.parseExpr()
		self.symbolTable[varname] = value
		return self.symbolTable[varname]

	"""
	
	 Parser.parseFunction(self)
	
	 This method will parse a function. The syntax for a function is as specified.
	 "fn" VAR ( VAR... ) ( statement... )
	 
	 @param self This instance of the Parser class.
	 @return The function, which is a python dictionary with an "args" field and a "statements" field.
	
	"""
	def parseFunction(self):
		self.expectLexeme('fn')
		fnname = self.tokens[self.pos].getLexeme()
		self.pos += 1
		args = []
		self.expectLexeme('(')
		while not self.end() and self.tokens[self.pos].getType() == 'VAR':
			args.append(self.tokens[self.pos].getLexeme())
			self.pos += 1
		self.expectLexeme(')')
		statements = []
		self.expectLexeme('(')
		numLeftBraces = 1
		statements.append(self.pos)
		while not self.end() and numLeftBraces > 0:
			if self.tokens[self.pos].getLexeme() == '(':
				numLeftBraces += 1
			elif self.tokens[self.pos].getLexeme() == ')':
				numLeftBraces -= 1
			self.pos += 1
		self.pos -= 1
		statements.append(self.pos)
		self.expectLexeme(')')
		self.symbolTable[fnname] = {
			'args':args,
			'statements':statements
		}
		return self.symbolTable[fnname]

	"""
	
	 Parser.parseWhile(self)
	 
	 This function will parse a while statement. The syntax for a while statement is as follows:
	 "while" expr ( statement... )
	 
	 @param self This instance of the Parser class.
	 @return The result of evaluating the while statement
	         (the result of the last statement evaluated in the while statement's body).
	
	"""
	def parseWhile(self):
		self.expectLexeme('while')	
		pos = self.pos
		while True:
			result = self.parseExpr()
			if result == 0:
				break
			elif type(result) is str and len(result) == 0:
				break
			self.expectLexeme('(')
			while not self.end() and self.tokens[self.pos].getLexeme() != ')':
				self.parseStatement()
			self.pos = pos
		self.expectLexeme('(')
		numLeftBraces = 1
		while not self.end() and numLeftBraces > 0:
			if self.tokens[self.pos].getLexeme() == '(':
				numLeftBraces += 1
			elif self.tokens[self.pos].getLexeme() == ')':
				numLeftBraces -= 1
			self.pos += 1

	"""
	
	 Parser.parseStatement(self)
	 
	 This function checks the current token and calls the appropriate function.
	 
	 @param self This instance of the Parser class.
	 @return The result of parsing the appropriate statement.
	
	"""
	def parseStatement(self):
		if self.tokens[self.pos].getLexeme() == 'set':
			return self.parseAssignment()
		elif self.tokens[self.pos].getLexeme() == 'fn':
			return self.parseFunction()
		elif self.tokens[self.pos].getLexeme() == 'while':
			return self.parseWhile()
		elif self.tokens[self.pos].getLexeme() == 'call':
			return self.parseCall()
		elif self.tokens[self.pos].getLexeme() == 'if':
			return self.parseIf()
		elif self.tokens[self.pos].getLexeme() in ['raw_python_eval', 'raw_python_exec']:
			return self.parseRawPython(self.tokens[self.pos].getLexeme()[11:])
		else:
			return self.parseExpr()

	"""
	
	 Parser.parse(self)
	 
	 This function will parse a program statement by statement.
	 
	 @param self This instance of the Parser class.
	 @return An array which contains the result of each statement's execution.
	
	"""
	def parse(self):
		results = []
		while not self.end():
			results.append(self.parseStatement())
		return results
