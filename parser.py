from lexer import Token, Tokenizer

class ParsingException(Exception):
	pass

class Parser:

	def __init__(self, tokens):
		self.tokens = tokens
		self.pos = 0
		self.symbolTable = {}

	def end(self):
		return self.pos >= len(self.tokens)

	def expectType(self, type_):
		if not self.end() and self.tokens[self.pos].getType() == type_:
			self.pos += 1
			return self.tokens[self.pos - 1]
		raise ParsingException('Expected type {}, got {}.'.format(type_, self.tokens[self.pos].getType()))

	def expectLexeme(self, lexeme):
		if not self.end() and self.tokens[self.pos].getLexeme() == lexeme:
			self.pos += 1
			return self.tokens[self.pos - 1]
		raise ParsingException('Expected lexeme {}, got {}.'.format(lexeme, self.tokens[self.pos].getLexeme()))

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
				new_python_src += str(self.symbolTable[python_src[start:end]])
				i = end
			else:
				new_python_src += python_src[i]
			i += 1
		if _type == 'exec':
			return exec(new_python_src)
		return eval(new_python_src)

	def parseArray(self):
		self.expectLexeme('array')
		self.expectLexeme('(')
		values = []
		while not self.end() and self.tokens[self.pos].getLexeme() != ')':
			values.append(self.parseExpr())
		self.expectLexeme(')')
		return values

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
				return self.symbolTable[self.tokens[self.pos - 1].getLexeme()]
		
		raise ParsingException('Excepted base, got {}'.format(self.tokens[self.pos].getLexeme()))

	def parseAtom(self):
		result = self.parseBase()
		while not self.end() and self.tokens[self.pos].getLexeme() in Tokenizer.ATOM_OPERATORS:
			op = self.expectType('OPR').getLexeme()
			result = eval('result' + str(op) + str(self.parseBase()))
		return result

	def parseExpr(self):
		result = self.parseAtom()
		while not self.end() and self.tokens[self.pos].getLexeme() in Tokenizer.EXPR_OPERATORS:
			op = self.expectType('OPR').getLexeme()
			self.pos += 1
			result = eval('result' + op + self.parseAtom())
		return result

	def parseAssignment(self):
		self.expectLexeme('set')
		varname = self.tokens[self.pos].getLexeme()
		self.pos += 1
		self.expectLexeme('=')
		value = self.parseExpr()
		self.symbolTable[varname] = value
		return self.symbolTable[varname]

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
		statements.append(self.pos)
		while not self.end() and self.tokens[self.pos].getLexeme() != ')':
			self.pos += 1
		statements.append(self.pos)
		self.expectLexeme(')')
		self.symbolTable[fnname] = {
			'args':args,
			'statements':statements
		}
		return self.symbolTable[fnname]

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
		self.expectLexeme(')')

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

	def parse(self):
		results = []
		while not self.end():
			results.append(self.parseStatement())
		return results
