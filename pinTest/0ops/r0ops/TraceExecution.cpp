#include <pin>
#include <iostream>
using namespace std;

FILE *LogFile;

ADDRINT StartAddr = 0;
ADDRINT EndAddr = 0;

void LogBasicBlock(ADDRINT ip){
	if(StartAddr == 0 && EndAddr == 0)
	{
		//exe还未加载
		return;
	}
	if(ip > EndAddr || ip < StartAddr)
	{
		//不在exe代码之内
		return;
	}
	UINT32 *CallArg = (UINT32 *)ip;
	string nameFunc = "";
	try{
		string nameFunc = RTN_FindNameByAddress(ip);
	}
	catch (int e){
		cout << "Exception Nr. " << e << endl;
	}

	fprintf(LogFile, "%p\n", ip);
	/*if(nameFunc == "" || nameFunc == "unnamedImageEntryPoint"){
		fprintf(LogFile, "loc_%p @ ???\n", ip);
	} else {
		fprintf(LogFile, "loc_%p @ %s\n", ip, nameFunc);
	}
	*/
}

void Trace(TRACE trace, void *v) {
	/* Iterate through basic blocks */
	for(BBL bbl = TRACE_BblHead(trace); BBL_Valid(bbl); bbl = BBL_Next(bbl)){
		/* Instrument at basic block level */
		INS head = BBL_InsHead(bbl);
		INS_InsertCall(head, IPOINT_BEFORE, AFUNPTR(LogBasicBlock), IARG_INST_PTR, IARG_END);
	}
}

bool FilterImg(string imageName)
{
	string postfix = imageName.substr(imageName.length()-3, 3);
	//OutFile << postfix << endl;
	if(postfix == "exe")
	{
		//OutFile << "find exe" << endl;
		return true;
	}
	return false;
}


VOID imageLoad_cb(IMG img, VOID *v)
{
	string imgName = IMG_Name(img);
	if(FilterImg(imgName))
	{
		StartAddr = IMG_StartAddress(img);
		EndAddr= StartAddr + IMG_SizeMapped(img);
	}
		
}


INT32 Usage()
{
	cerr << "This tool prints out the number of dynamically executed " << endl <<
		"instructions, basic blocks and threads in the application." << endl << endl;

	cerr << KNOB_BASE::StringKnobSummary() << endl;

	return -1;
}

VOID Fini(INT32 code, VOID *v)
{
	fclose(LogFile);
}


int main(int argc, char *argv[])
{
	/* Initialize Pin with symbol capabilities */
	PIN_InitSymbols();
	if(PIN_Init(argc, argv)) return Usage();
	LogFile = fopen("log.txt", "w");
	if(!LogFile)
	{
		cerr << "open log.txt error" << endl;
	}
	TRACE_AddInstrumentFunction(Trace, 0);  // basic block analysis
	IMG_AddInstrumentFunction(imageLoad_cb, 0); // image activities
	//PIN_AddThreadStartFunction(threadStart_cb, 0);  // thread start
	//PIN_AddThreadFiniFunction(threadFinish_cb, 0);  // thread end
	PIN_AddFiniFunction(Fini, 0);       // cleanup code

	PIN_StartProgram();     // This never returns

	return 0;
}