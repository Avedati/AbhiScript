class Token:

	def __init__(self, type_, lexeme):
		self.type_ = type_
		self.lexeme = lexeme

	def __str__(self):
		return '< ' + self.getType() + ', ' + self.getLexeme() + ' >'

	def getType(self):
		return self.type_

	def getLexeme(self):
		return self.lexeme

	def setType(self, type_):
		self.type_ = type_

	def setLexeme(self, lexeme):
		self.lexeme = lexeme

class Tokenizer:

	ATOM_OPERATORS = ['+', '-']
	EXPR_OPERATORS = ['*', '/', '%']
	TOKENS = ['=']
	PUNC = ['(',')']

	def __init__(self, source):
		self.source = source
		self.pos = 0

	def advance_while(self, test):
		lexeme = ''
		while not self.end() and test(self.source[self.pos]):
			lexeme += self.source[self.pos]
			self.pos += 1
		return lexeme

	def end(self):
		return self.pos >= len(self.source)

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
