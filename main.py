from lexer import Token, Tokenizer
from parser import Parser
import sys

if __name__ == '__main__':

	__pre__ = '''
		fn print(arg) ( raw_python_exec \"print('#__arg#')\" )
		fn eq(a b)  ( raw_python_eval \"1 if #__a# == #__b# else 0\" )
		fn neq(a b) ( raw_python_eval \"0 if #__a# == #__b# else 1\" )
		fn assert_eq(vb vl) ( if call neq(vb vl) ( raw_python_exec \"raise Exception('Assertion failed: #__vb# does not equal #__vl#')\" ) )
		fn access(arr idx) ( raw_python_eval \"#__arr#[#__idx#]\" )
	'''
	source = __pre__

	if len(sys.argv) >= 2:
		with open(sys.argv[1], 'r') as fp:
			source += fp.read()

	tokenizer = Tokenizer(source)
	tokens = tokenizer.tokenize()
	parser = Parser(tokens)
	result = parser.parse()
