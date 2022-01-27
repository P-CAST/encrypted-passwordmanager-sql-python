@echo off

set sourcefile=%1
IF [%sourcefile%]==[] ( goto :NO_PARAMS ) ELSE ( goto :OPERATE )

:NO_PARAMS
    echo No sourcefile specified
    exit 1

:OPERATE
    pyinstaller --onefile %sourcefile%.py >NUL  2>NUL
    del "%sourcefile%.spec" 
    @RD /S /Q "build"  
    @RD /S /Q "__pycache__"
    copy .\dist\%sourcefile%.exe .\ >NUL 2>NUL
    @RD /S /Q "dist"
    goto :DONE

:DONE
    echo Sourcefile compiled successfully
    pause