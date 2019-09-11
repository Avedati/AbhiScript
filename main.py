from lexer import Token, Tokenizer
from parser import Parser
import sys

if __name__ == '__main__':

	__pre__ = ''' fn print(arg) ( raw_python_exec \"print('#__arg#')\" ) '''
	source = __pre__

	if len(sys.argv) >= 2:
		with open(sys.argv[1], 'r') as fp:
			source += fp.read()

	tokenizer = Tokenizer(source)
	tokens = tokenizer.tokenize()
	parser = Parser(tokens)
	result = parser.parse()
