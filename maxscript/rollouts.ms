-- convert maxscript value to python value 
fn mxsPyEscapeStr val =
(
	substituteString val @"\" @"\\"
)

fn mxsPyConvertVal val =
(
	result = "None"
	
	case ( classof val ) of
	(
		BooleanClass:
		(
			if val == true then result = "True"
			else result = "False"
		)
		String: result = "\"" + mtEscapeStr( val ) + "\""
		default: result = val as string
	)
	
	result
)

-- execute a python function from maxscript
fn mxsPyExec module func args =
(
	local code = ""
	
	if module != undefined then
		code += module + "."
	
	code += func + "("
	if args.count > 0 do
	(
		code += mxsPyConvertVal( args[1] )
		
		for i = 2 to args.count do
			code += ", " + mxsPyConvertVal( args[i] )

	)
	
	code += ")"
	
	print code
	python.execute code
)

rollout yafeAboutRollout "About"
(
    label lblAbout "yafe plugin for 3ds Max" across:1
    label lblAbout2 "Persona 5 FBN/HTB importer and exporter" across:1
    label lblAbout3 "Version 0.1" across:1
    label lblAbout4 "© 2021 TGE" across:1
) 

rollout yafeIORollout "Import/Export"
(
    label lblExport "Note: Select FBN root object before export" across:1
	checkbox chkFlip "Flip up axis" align:#center across:1
    button btnImport "Import" align:#center across:2
    button btnExport "Export" align:#center across:2

	on chkFlip changed state do mxsPyExec "yafeIORollout" "chkFlipChanged" #(state)
    on btnImport pressed do mxsPyExec "yafeIORollout" "btnImportPressed" #()
    on btnExport pressed do mxsPyExec "yafeIORollout" "btnExportPressed" #() 
)