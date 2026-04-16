from ctypes         import windll, create_unicode_buffer
from binaryninja    import PluginCommand, InstructionTextTokenType as IT3
from binaryninjaui  import UIContext

def cast(bv = None, _ = None) -> int:
    
    if (ctx := UIContext.activeContext()): 
        ctx = ctx.contentActionHandler().actionContext()
    else: return -1

    # no "all()" bc. it uses walrus-syntax
    if not (cur := ctx.token).valid              \
    or not (cur.token.type == IT3.IntegerToken)  \
    or not (0 < (tkn := cur.token.value) < 16000): 
        return -1
    
    return tkn

def resolve(code: int) -> str | None:

    buf = create_unicode_buffer(256)
    windll.kernel32.FormatMessageW\
    (
        0x1000, # dwFlags
        None,   # lpSource
        cast(), # dwMessageId
        0,      # dwLanguageId
        buf,    # lpBuffer
        256,    # nSize
        None    # *Arguments
    )

    if buf: return buf.value.strip()

if __name__ != "__main__":
    
    nc = 'Resolve Error Code and ...'
    cc = '0x%x (%d) resolves to "%s"'

    verify = lambda x, y : cast(x, y) != -1
    logger = lambda x, y : print(cc % (n:=cast(), n, resolve(n)))
    invoke = lambda x, y : windll.user32.MessageBoxW(0, resolve(cast()),'', 64)
    inplce = lambda x, y : x.set_comment_at(y, cc % (n:=cast(), n, resolve(n)))

    PluginCommand.register_for_address(f"{nc}\\Insert as Comment", '', inplce, verify)
    PluginCommand.register_for_address(f"{nc}\\Insert in Logging", '', logger, verify)
    PluginCommand.register_for_address(f"{nc}\\Invoke as MsgBoxW", '', invoke, verify)