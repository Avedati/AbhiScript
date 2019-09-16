"""

 class Token

 This is a class that representes a single token lexed by the tokenizer. It has two fields, a type and a lexeme.

"""

class Token:

	"""
	
	 Token.__init__(self, type_, lexeme)
	 
	 This function is called whenever a new token is created.
	 
	 @param self This instance of the token class.
	 @param type_ The type of the token.
	 @param lexeme The lexeme of the token (the string of characters that was consumed by the tokenizer).
	
	"""
	
	def __init__(self, type_, lexeme):
		self.setType(type_)
		self.setLexeme(lexeme)

	"""
	
	 Token.__str__(self)
	 
	 This function is called whenever the Token object is converted to a string (for example, when it is printed).
	 
	 @param self This instance of the Token class.
	 @return A string representation of this token.
	
	"""
		
	def __str__(self):
		return '< ' + self.getType() + ', ' + self.getLexeme() + ' >'

	"""
	
	 Token.getType(self)
	 
	 This is a safe getter method for the type_ field of the Token class.
	 
	 @param self This instance of the Token cass.
	 @return The type_ field.
	
	"""
	
	def getType(self):
		return self.type_
	
	"""
	
	 Token.getLexeme(self)
	 
	 This is a safe getter method for the lexeme field of the Token class.
	 
	 @param self This instance of the Token cass.
	 @return The lexeme field.
	
	"""
	
	def getLexeme(self):
		return self.lexeme

	"""
	
	 Token.setType(self, type_)
	 
	 This is a safe setter method for the type_ field of the Token class.
	 
	 @param self This instance of the Token class.
	
	"""
	
	def setType(self, type_):
		self.type_ = type_

	"""
	
	 Token.setLexeme(self, lexeme)
	 
	 This is a safe setter method for the lexeme field of the Token class.
	 
	 @param self This instance of the Token class.
	
	"""
		
	def setLexeme(self, lexeme):
		self.lexeme = lexeme

"""

 class Tokenizer

 This is a class that handles lexing an input string, turning it into the appropriate tokens for the Stork programming language.

"""
class Tokenizer:

	ATOM_OPERATORS = ['+', '-'] # The valid operators that can act on a base (a number, string, variable, or function call).
	EXPR_OPERATORS = ['*', '/', '%'] # The valid operators that can act on an atom (an base + or - a base).
	TOKENS = ['='] # Other tokens
	PUNC = ['(',')'] # Punctuation marks

	"""
	
	 Tokenizer.__init__(self, source)
	 
	 This function is called when a new Tokenizer object is created.
	 
	 @param self This instance of the Tokenizer class.
	 @param source The source string to be interpreted by the Stork interpreter.
	
	"""
	
	def __init__(self, source):
		self.source = source
		self.pos = 0

	"""
	
	 Tokenizer.advance_while(self, test)
	 
	 This function will consume characters from the source string as long as they return True based on a test function.
	 
	 @param self This instance of the Tokenizer class.
	 @param test A function that takes a character and returns either True or False.
	 @return The characters that were read and consumed.
	
	"""
		
	def advance_while(self, test):
		lexeme = ''
		while not self.end() and test(self.source[self.pos]):
			lexeme += self.source[self.pos]
			self.pos += 1
		return lexeme

	"""
	
	 Tokenizer.end(self)
	 
	 This function returns True if the current position of the tokenizer is at or past the end of the source string.
	 
	 @param self This instance of the Tokenizer class.
	 @return Whether or not our tokenizer's current position is outside of the source string.
	
	"""
	
	def end(self):
		return self.pos >= len(self.source)

	"""
	
	 Tokenizer.tokenize(self)
	 
	 This function will tokenize the source string (converting it into a list of tokens).
	 
	 @param self This instance of the Tokenizer class.
	 @return An array of tokens.
	
	"""
	
	def tokenize(self):
		tokens = []
		while not self.end():
			if self.source[self.pos].isdigit() or self.source[self.pos] == '.':
				tokens.append(Token('NUM', self.advance_while(lambda ch: ch.isdigit() or ch == '.')))
				self.pos -= 1
			elif self.source[self.pos] in '\'"':
				end = self.source[self.pos]
				self.pos += 1
				tokens.append(Token('STR', self.advance_while(lambda ch: ch != end)))
			elif self.source[self.pos].isalpha() or self.source[self.pos] == '_':
				tokens.append(Token('VAR', self.advance_while(lambda ch: ch.isalnum() or ch == '_')))
				self.pos -= 1
			else:
				for op in Tokenizer.ATOM_OPERATORS:
					if self.pos + len(op) <= len(self.source) and self.source[self.pos:self.pos+len(op)] == op:
						self.pos += len(op) - 1
						tokens.append(Token('OPR', op))
						break

				for op in Tokenizer.EXPR_OPERATORS:
					if self.pos + len(op) <= len(self.source) and self.source[self.pos:self.pos+len(op)] == op:
						self.pos += len(op) - 1
						tokens.append(Token('OPR', op))
						break

				for tk in Tokenizer.TOKENS:
					if self.pos + len(tk) <= len(self.source) and self.source[self.pos:self.pos+len(tk)] == tk:
						self.pos += len(tk) - 1
						tokens.append(Token('TKN', tk))
						break

				for pn in Tokenizer.PUNC:
					if self.pos + len(pn) <= len(self.source) and self.source[self.pos:self.pos+len(pn)] == pn:
						self.pos += len(pn) - 1
						tokens.append(Token('PNC', pn))
						break

			self.pos += 1
		return tokens
