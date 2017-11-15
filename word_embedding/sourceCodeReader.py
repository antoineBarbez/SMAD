# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
import fnmatch

from pygments.token import *
from pygments.lexers import JavaLexer

TOKEN_TYPES = {
	Token:                         0,

	Text:                          0,
	Whitespace:                    0,
	Escape:                        0,
	Error:                         0,
	Other:                         1,

	Keyword:                       1,
	Keyword.Constant:              1,
	Keyword.Declaration:           1,
	Keyword.Namespace:             1,
	Keyword.Pseudo:                1,
	Keyword.Reserved:              1,
	Keyword.Type:                  1,

	Name:                          0,
	Name.Attribute:                0,
	Name.Builtin:                  0,
	Name.Builtin.Pseudo:           0,
	Name.Class:                    0,
	Name.Constant:                 0,
	Name.Decorator:                0,
	Name.Entity:                   0,
	Name.Exception:                0,
	Name.Function:                 0,
	Name.Function.Magic:           0,
	Name.Property:                 0,
	Name.Label:                    0,
	Name.Namespace:                0,
	Name.Other:                    0,
	Name.Tag:                      0,
	Name.Variable:                 0,
	Name.Variable.Class:           0,
	Name.Variable.Global:          0,
	Name.Variable.Instance:        0,
	Name.Variable.Magic:           0,

	Literal:                       0,
	Literal.Date:                  0,

	String:                        0,
	String.Affix:                  0,
	String.Backtick:               0,
	String.Char:                   0,
	String.Delimiter:              0,
	String.Doc:                    0,
	String.Double:                 0,
	String.Escape:                 0,
	String.Heredoc:                0,
	String.Interpol:               0,
	String.Other:                  0,
	String.Regex:                  0,
	String.Single:                 0,
	String.Symbol:                 0,

	Number:                        0,
	Number.Bin:                    0,
	Number.Float:                  0,
	Number.Hex:                    0,
	Number.Integer:                0,
	Number.Integer.Long:           0,
	Number.Oct:                    0,

	Operator:                      1,
	Operator.Word:                 1,

	Punctuation:                   0,

	Comment:                       0,
	Comment.Hashbang:              0,
	Comment.Multiline:             0,
	Comment.Preproc:               0,
	Comment.PreprocFile:           0,
	Comment.Single:                0,
	Comment.Special:               0,

	Generic:                       0,
	Generic.Deleted:               0,
	Generic.Emph:                  0,
	Generic.Error:                 0,
	Generic.Heading:               0,
	Generic.Inserted:              0,
	Generic.Output:                0,
	Generic.Prompt:                0,
	Generic.Strong:                0,
	Generic.Subheading:            0,
	Generic.Traceback:             0,
}

def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=50):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """
    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),

    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def readData():
	print("Loading the training dataset...")
	nbFiles = 0
	for path,dirs,files in os.walk('./java_softwares'):
		for f in fnmatch.filter(files,'*.java'):
			nbFiles = nbFiles + 1

	print("Number of files :", nbFiles)
	print_progress(0, nbFiles, prefix = 'Progress:', suffix = 'Complete')


	lexer = JavaLexer()
	data = []
	count = 0
	for path,dirs,files in os.walk('./java_softwares'):

		for f in fnmatch.filter(files,'*.java'):
			count = count + 1
			fullname = os.path.abspath(os.path.join(path,f))
        	

			with open(fullname,'r') as inputText:
				text = inputText.read()
			tokens = lexer.get_tokens_unprocessed(text)

			for token in tokens:
				idx = TOKEN_TYPES.get(token[1], 1) + 1
				stringToken = str(token[idx])
				data.append(stringToken)

			if count % 50 == 0:
				print_progress(count, nbFiles, prefix = 'Progress:', suffix = 'Complete')

	print_progress(nbFiles, nbFiles, prefix = 'Progress:', suffix = 'Complete')
	return data


if __name__ == "__main__":
	data = readData()
	#print(data[:30])
	print(set(data))
	print(len(data))
	print(len(set(data)))