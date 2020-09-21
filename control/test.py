# def MyTestFun(args):
#    print('args', args)


def MyTestFun(args1=99, args2=150):
    print('locals var: ',locals())
    print('res args', args1,' args2:',args2)

def MyTestFun2(args):
    print('args', args)
    return "OK--1"
