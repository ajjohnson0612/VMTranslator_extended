import re 
def valid(line):
    """ Line valid or not? """
    line = line.strip()
    if not line:
        return False
    if line.startswith('//'):
        return False
    
        
    return True

def clean_lines(lines):
    lines = [line.strip() for line in lines]
    lines = [line.split('//')[0].strip() for line in lines if valid(line)]
    return lines

def initialization(filename):
    """
    Initialize base addresses.
    """
    ret = ['@256', 'D=A', '@SP', 'M=D']
    ret.extend(process_call("Sys.init",0, filename, 0,0))
    return ret

def process_push_pop(command, arg1, arg2, fname, l_no):
    mapping = {'local':'@LCL', 'argument':'@ARG', 'this':'@THIS','that':'@THAT', 
               'static':16, 'temp' : 5, 'pointer': 3}
    ret = []
    comp = (int(arg2))
    if comp >= 32768:
        print("To large of number at File {}, Line {}".format(fname, l_no))
    if comp < 0 :
        print('Invalid location for push or pop. File {}. Line {}'.format(fname, l_no))
    if arg1 == 'constant':
        if command == 'pop':
            ret.extend([
            '@{}'.format(arg2),
            ])
    elif arg1 == 'static':
        ret.extend([
            '@{}.{}'.format(fname, arg2) 
        ])
    elif arg1 == 'ram':
        ret.extend([
            '@{}'.format(arg2)])


    elif arg1 in ('temp', 'pointer'):
        if int(arg2) > 10 and arg1 == 'pointer':
            print('Invalid location for segment. File {}. Line {}'.format(fname, l_no))
        elif int(arg2) > 7 and arg1 == 'temp':
            print('Invalid location for segment. FIle {}, Line {}'.format(fname,l_no))
        ret.extend([
            '@R{}'.format(mapping.get(arg1)+int(arg2))
        ])
    elif arg1 in ('local', 'argument', 'this', 'that'):
        ret.extend([
            mapping.get(arg1), 'D=M', '@{}'.format(arg2), 'A=D+A'
        ])
    else:
        print('{} is invalid memory segment. File {}. Line {}'.format(arg1, fname, l_no))
    
    if command == 'push':
        if arg1 == 'constant':
            ret.append('D=A')
        if arg1 == 'ram':
            ret.append('D=M')
        else:
            ret.append('D=M')
        ret.extend([
            '@SP', 'A=M', 'M=D', # *SP = *addr
            '@SP', 'M=M+1' # SP++
        ])
    else:
        ret.extend(['D=A', 
            '@R13', 'M=D', # addr stored in R13
            '@SP', 'AM=M-1', # SP--
            'D=M', # D = *SP
            '@R13', 'A=M', 'M=D' # *addr = D = *SP
        ])
    
    return ret


def process_arithmetic(command, filename, l_no, state):
    ret = []
    symb = {'add':'+', 'sub':'-', 'and':'&', 'or':'|', 'neg': '-', 'not':'!', 'eq':'JNE', 'lt':'JGE', 'gt':'JLE', 'le' : 'LTE' , 'ge': 'GTE', 'ne' : '!='}

    if command in ('neg', 'not', 'ne'): # unary operators
        ret.extend([
            '@SP', 'A=M-1', # SP--
            'M={}M'.format(symb.get(command)) ])
    if command in ('l-or'):
       ret.extend([
            '@SP',
            'AM=M-1',
            'D=M',
            '@{}true{}'.format(state[2],state[0]),
            'D;JNE',
            '@SP',
            'AM=M-1',
            'M=0'
            '@{}continue{}'.format(state[2],state[0]),
            '0;JMP',
            '({}true{})'.format(state[2],state[0]),
            '@SP',
            'AM=M-1',
            'M=-1',
            '({}continue{})'.format(state[2],state[0]),
            '@SP'
            'M=M+1'])
    if command in ('bool'):
      ret.extend([         
      '@SP',
      'AM=M-1',
      'D=M',
      '@{}END_BOOL_{}'.format(state[2],state[0]),
      'D;JEQ',
      '@SP',
      'A=M',
      'M=-1',
      '({}END_BOOL_{})'.format(state[2],state[0]),
      '@SP',
      'M=M+1'
      ])
    if command in ('l-not'):
      ret.extend([
        '@SP',  
        'AM=M-1',
        'D=M',
        '@{}val_eq_0{}'.format(state[2],state[0]), 
        'D;JEQ',
        '@SP',
        'A=M',
        'M=0',
        '@{}continue{}'.format(state[2],state[0]),
        '0;JMP',
        '({}val_eq_0{})'.format(state[2],state[0]),
        '@SP',
        'A=M',
        'M=-1',
        '({}continue{})'.format(state[2],state[0]),
        '@SP',
        'M=M+1'
      ])
    if command in ('l-and'):
      ret.extend([
        '@SP', 
        'AM=M-1',
        'D=M', 
        '@{}False{}'.format(state[2],state[0]),
        'D;JEQ',
        '@SP',
        'A=M-1',
        'D=M',
        '@{}False{}'.format(state[2],state[0]),
        'D;JEQ',
        '@SP', 
        'AM=M-1',
        'M=-1',
        '@{}Continue{}'.format(state[2],state[0]),
        '0;JMP',
        '({}False{})'.format(state[2],state[0]),
        '@SP', 
        'AM=M-1',
        'M=0',
        '({}Continue{})'.format(state[2],state[0]),
        '@SP',
        'M=M+1'
      ])
    if command in ('l-xor'):
      ret.extend([          
            '@SP',
            'AM=M-1',
            'D=M',
            '@FIRSTTRUE_{}'.format(state[0]),
            'D;JNE',
            '@SP',
            'AM=M-1',
            'D=M',
            '@FIRSTFALSE_SECNDTRUE_{}'.format(state[0]),
            'D;JNE',
            '@SP',
            'A=M',
            'M=0',
            '@CONT_{}'.format(state[0]),
            '0;JMP',
            '(FIRSTTRUE_{})'.format(state[0]),
            '@SP',
            'AM=M-1',
            'D=M',
            '@SECONDTRUE_{}'.format(state[0]),
            'D;JNE',
            '@SP',
            'A=M',
            'M=-1',
            '@CONT_{}'.format(state[0]),
            '0;JMP',
            '(SECONDTRUE_{})'.format(state[0]),
            '@SP',
            'A=M',
            'M=0',
            '@CONT_{}'.format(state[0]),
            '0;JMP',
            '(FIRSTFALSE_SECNDTRUE_{})'.format(state[0]),
            '@SP',
            'A=M',
            'M=-1',
            '(CONT_{})'.format(state[0]),
            '@SP',
            'M=M+1'])


    if command in ('add', 'sub', 'or'):
        ret.extend([
        '@SP', 
        'AM=M-1', # SP--,
        'D=M', 
        'A=A-1'
        ])
        ret.append('M=M{}D'.format(symb.get(command)))

    elif command in ('eq', 'gt', 'lt','le','ge','ne'):
        ret.extend([
            '@SP', 
            'AM=M-1', # SP--,
            'D=M', 
            'A=A-1'
            'D=M-D',
            '@FALSE_{}'.format(state[0]), # Jump to make M=1 if condition is true
            'D;{}'.format(symb.get(command)), 
            '@SP', 'A=M-1', 'M=-1', '@CONTINUE_{}'.format(state[0]), '0;JMP', # if above condition is false, M=0
            '(FALSE_{})'.format(state[0]), '@SP', 'A=M-1', 'M=0', # if condition is true
            '(CONTINUE_{})'.format(state[0])
        ])
        state[0] += 1
    if not ret:
        print("Unkown logical operator {}, Line {}".format(command,l_no))
        
    
    # ret.extend(['@SP', 'M=M+1']) # SP++
    
    return ret


def process_call(arg1, arg2, filename, call_count, l_no):
    if re.match("^[0-9]*$",(str(call_count))) == None:
        print('Invalid number of local/args File {}, Line{}, Args: {}'.format(filename,l_no,arg2))
    
    new_label = '{}.RET_{}'.format(filename, call_count)
    ret = [
        '@{}'.format(new_label),
        'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'
    ]
    for address in ['@LCL', '@ARG', '@THIS', '@THAT']:
        ret.append(address)
        ret.extend(['D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'])
    
    ret.extend(['@SP', 'D=M', '@LCL', 'M=D'])
    # D aleady holds SP
    ret.extend(['@{}'.format(int(arg2)+5), 'D=D-A', '@ARG', 'M=D']) 
    ret.extend(['@{}'.format(arg1), '0;JMP']) # goto f
    ret.append('({})'.format(new_label))
    return ret


def process_return():
    #FRAME = '@R14'
    #RET   = '@R15'
    ret = [
        '@LCL', 'D=M', '@R14', 'M=D', # FRAME = LCL
        # FRAME, 'D=M', '@5', 'D=D-A',  'A=D', 'D=M', RET, 'M=D', # RET = *(FRAME-5),
        '@5', 'A=D-A', 'D=M', '@R15', 'M=D', # RET = *(FRAME-5),
        '@ARG', 'D=M', '@0', 'D=D+A', '@R13', 'M=D', '@SP', 'AM=M-1', 'D=M', '@R13', 'A=M', 'M=D', # *ARG = pop()
        '@ARG', 'D=M', '@SP', 'M=D+1' # SP = ARG + 1
    ]
    for addr in ['@THAT', '@THIS', '@ARG', '@LCL']:
        ret.extend([
            '@R14', 'AMD=M-1', # 'D=M-1', 'AM=D'
             'D=M', # D holds *(FRAME - (i+1))
            addr, 'M=D'
        ])
    ret.extend(['@R15', 'A=M', '0;JMP'])
    return ret

def process_function(arg1, arg2,l_no,filename):
    if(re.match("^[A-Za-z0-9_.-]*$",arg1) == None):
        print('Invalid function name File: {}, Line: {}, Name: {}'.format(filename,l_no,arg1))
        return " "
    if (re.match("^[0-9]*$",arg2) == None):

        print ("Illegal count, for function {}{}, line {}, file {}".format(arg1,arg2,l_no,filename))
        return " "
    ret = ['({})'.format(arg1)]
    for _ in range(int(arg2)):
        ret.extend([
             '@0', 'D=A',
            '@SP', 'A=M', 'M=D', 
            '@SP', 'M=M+1'
        ])
    
    return ret


def process_line(line, filename, l_no, state):
    tokens = line.strip().split()
    command = tokens[0]
    
    if len(tokens) == 1:
        if command == 'return':
            ret = process_return()
            #state[2] = ''
        elif command in ('add', 'sub', 'neg', 'eq', 'gt', 'lt', 'l-and', 'l-or', 'l-not', 'le','ge','ne','l-xor','bool','not'):
            ret = process_arithmetic(command, filename, l_no, state)
        else:
            print("{} is not a valid command. File {}. Line {}".format(command, filename, l_no))
            return ' ' 
    elif len(tokens) == 2:
        if re.match("^[A-Za-z0-9_.-]*$",tokens[1]) == None:
            print("error invalid label/goto/if-goto name Line{}: File:{} Content:{}".format(l_no,filename,line))
        
        if command == 'label':
            ret = ['({}{})'.format(state[2], tokens[1])]
        elif command == 'goto':
            ret = ['@{}{}'.format(state[2], tokens[1]), '0;JMP']
        elif command == 'if-goto':
            ret = ['@SP','M=M-1','A=M','D=M', '@{}{}'.format(state[2], tokens[1]), 'D;JNE']
        else:
            print("Incorrect format at Line {}, File {}, Content {}".format(l_no,filename,line))
            return " "
        if re.search('^\s*[0-9]',(str(tokens[1]))) != None:      
          print("Invalid label name, Line {}, FIle {}, Content {}".format(l_no,filename,line))
    elif len(tokens) == 3:
        if command in ('push', 'pop'):
            ret = process_push_pop(*tokens, filename, l_no)
        elif command == 'call':
            ret = process_call(tokens[1], tokens[2], filename, state[1],l_no)
            state[1] += 1
        elif command == 'function':
            ret = process_function(tokens[1], tokens[2],l_no,filename)
            state[2] = '{}$'.format(tokens[1])
        else:
            print("{} is not a valid command. File {}. Line {}".format(command, filename, l_no))
            return " "
    
    else:
        print("{} is not a valid command. File {}. Line {}".format(command, filename, l_no))
        return " "
    return ret


def process_file(filename):
    with open(filename, 'r+') as f:
        vm_code = clean_lines(f.readlines())
    
    filename = os.path.split(filename)[-1]
    filename = filename.replace('.vm', '')
    state = [0, 0, ''] # bool_count, num_of_calls and func_state
    
    output = [x for i, line in enumerate(vm_code) for x in process_line(line, filename, i, state)]
    #for i, line in enumerate(vm_code):
    #    tmp = process_line(line, fname, i, bool_count)
    #    output.extend(tmp)
    return output

def translate_vm_to_asm(inp, outname=None):
    is_dir = False
    if os.path.isdir(inp):
        is_dir = True
        if not outname:
            if inp.endswith('/'):
                inp = inp[:-1]
            outname = '{}.asm'.format(os.path.split(inp)[-1])
            outname = os.path.join(inp, outname)
    else:
        if not outname:
            outname = '{}.asm'.format(os.path.splitext(inp)[0])
    
    
    #output, bool_count = initialization(), [0]
    output = initialization(os.path.splitext(os.path.split(outname)[-1])[0])
    if is_dir:
        for file in os.listdir(inp):
            pth = os.path.join(inp, file)
            if not os.path.isfile(pth):
                continue
            if os.path.splitext(pth)[-1] != '.vm':
                continue
            with open(pth, 'r+') as f:
                vm_code = clean_lines(f.readlines())
            
            tmp = process_file(pth)
            output.extend(tmp)
            
    else:
        output.extend(process_file(inp))
    
    #output.extend(['(END)', '@END', '0;JMP'])
    out_str = '\n'.join(output)
    with open(outname, 'w') as f:
        f.write(out_str)


if __name__ == "__main__":
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser(
        description="Enter path of directory or file to translate")
    
    parser.add_argument('filename', action="store")
    parser.add_argument('-o', '--outfile' , action="store", default=None, dest='outname')
    parser.add_argument('-s', '--strict', action = "store", default = None, dest = 'strictness');
    args = parser.parse_args()
    fname = args.filename
    outname = args.outname
    strict = args.strictness
    if not os.path.exists(fname):
        print("Path doesn't exist")
        sys.exit()
    
    translate_vm_to_asm(fname, outname)
    print("File translated...\nHave fun.")
    
