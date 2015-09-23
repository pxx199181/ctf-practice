/*BEGIN_LEGAL 
Intel Open Source License 

Copyright (c) 2002-2015 Intel Corporation. All rights reserved.
 
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.  Redistributions
in binary form must reproduce the above copyright notice, this list of
conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.  Neither the name of
the Intel Corporation nor the names of its contributors may be used to
endorse or promote products derived from this software without
specific prior written permission.
 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE INTEL OR
ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
END_LEGAL */
/* ===================================================================== */
/*
  @ORIGINAL_AUTHOR: Robert Muth
*/

/* ===================================================================== */
/*! @file
 *  This file contains an ISA-portable PIN tool for counting dynamic instructions
 */

#include "stdlib.h"
#include <iostream>
#include <fstream>
#include "pin.H"
#include <string>
#include <vector>
#include <map>

ofstream OutFile;
ofstream DataFile;
int _vscprintf (const char * format, va_list pargs)
{ 
 int retval; 
 va_list argcopy;
 va_copy(argcopy, pargs); 
 retval = vsnprintf(NULL, 0, format, argcopy); 
 va_end(argcopy); 
 return retval;
}

void cz_Log(ofstream &OutFile, char const* format, ...)
{
    OutFile.flush();
    va_list arg_list;
    va_start(arg_list, format);

    char* buf;
    int size;
    size = _vscprintf(format, arg_list);
    if (size == -1) return;
    if (size == 0) return;
    ++size;
    buf = (char*)malloc(size * sizeof(char));
    if (buf == NULL) return;

    vsnprintf(buf, size, format, arg_list);
    OutFile.write(buf, size - 1);
    OutFile.flush();

    free(buf);
}

/* ===================================================================== */
/* Global Variables */
/* ===================================================================== */

KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool",
    "o", "pxxTest.out", "specify output file name");


ADDRINT StartAddr = 0xdead1f4;
ADDRINT EndAddr = 0xdead3b3;
bool record_once = false;
bool begin_to_record = false;

typedef struct tag_Instruction_Info {
    ADDRINT Addr;
    string Instruction;
} Instruction_Info;

int record_step = 0;

int count_ptr = 1;

vector<Instruction_Info> vecInstruction;
vector<Instruction_Info>::iterator itera;
ADDRINT last_ip = 0;
map<ADDRINT, vector<string> > show_args;
map<ADDRINT, string> disassemble_info;

VOID add_to_disassemble(ADDRINT ip, string disassemble_str)
{
	disassemble_info.insert(pair<ADDRINT, string>(ip, disassemble_str));
}
string disassemble(ADDRINT ip)
{
	map<ADDRINT,string>::iterator t_itera;
	t_itera = disassemble_info.find(ip);
	if (t_itera != disassemble_info.end())
		return t_itera->second;
	else
		return "(nil)";
}
#define REG_RAX 0
#define REG_RBX 1
#define REG_RCX 2
#define REG_RDX 3
#define REG_ESI 4
#define REG_EDI 5
#define REG_RSP 6
#define REG_RBP 6
vector<string> REG_VEC;
VOID init_regVec()
{
    REG_VEC.push_back("rax");
    REG_VEC.push_back("rbx");
    REG_VEC.push_back("rcx");
    REG_VEC.push_back("rdx");
    REG_VEC.push_back("esi");
    REG_VEC.push_back("edi");
    REG_VEC.push_back("rbp");
}

/* ===================================================================== */
/* Commandline Switches */
/* ===================================================================== */


/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

INT32 Usage()
{
    cerr <<
        "This tool prints out the number of dynamic instructions executed to stderr.\n"
        "\n";

    cerr << KNOB_BASE::StringKnobSummary();

    cerr << endl;

    return -1;
}

/* ===================================================================== */
int get_reg_index(string reg_str)
{
    unsigned int i;
    for (i = 0; i < REG_VEC.size(); i++)
    {
        if (REG_VEC[i] == reg_str)
            return i;
    }
    return -1;
}

VOID init_args()
{
    ADDRINT ip;
    vector<string> args;

    ip = 0xdead19f;
    args.push_back("rax");
    args.push_back("rbx");
    show_args.insert(pair<ADDRINT, vector<string> >(ip, args));

    ip = 0xdead1ae;
    args.clear();
    args.push_back("rax");
    args.push_back("rbx");
    show_args.insert(pair<ADDRINT, vector<string> >(ip, args));

}

VOID diy_init() 
{
    OutFile.open(KnobOutputFile.Value().c_str());
    DataFile.open("pxxTest.data");
    init_regVec();
    init_args();
}

VOID show_info(ADDRINT ip, ADDRINT rax, ADDRINT rbx){
    map<ADDRINT, vector<string> >::iterator t_itera;
    t_itera = show_args.find(ip);
    if (t_itera != show_args.end())
    {
        
        vector<string>::iterator each_args = t_itera->second.begin();
        while(each_args != t_itera->second.end())
        {
            switch(get_reg_index(*each_args))
            {
                case REG_RAX:cz_Log(OutFile, "rax = %x ", rax); break;
                case REG_RBX:cz_Log(OutFile, "rbx = %x ", rbx); break;
                default:cz_Log(OutFile, "no such reg:%s ", each_args->c_str()); break;
            }
            each_args++;
        }
        cz_Log(OutFile, "\n");
    }
}

char buff[20] = {0};
VOID doStepByStep(ADDRINT ip, ADDRINT len, ADDRINT rax, ADDRINT rbx)
{
    //check if begin to record
    if (ip == StartAddr && record_once == false) {
        begin_to_record = true;
        record_once = true;
    	cz_Log(OutFile, "begin\n");
    }

    //cz_Log(OutFile, "(+%6d)%p[size:%d]:%2d %s\n", count_ptr, itera->Addr, vecInstruction.size(), begin_to_record, itera->Instruction.c_str());
    
    if (begin_to_record) {
    	if (ip == EndAddr) {
    		begin_to_record = false;
    		cz_Log(OutFile, "end\n");
    		return;
    	}
    	//if (strcmp())
    	if (record_step < 5000) {
    		PIN_SafeCopy((void *)buff, (void *)ip, len);
    		record_step++;
    		cz_Log(OutFile, "%p: %s\n", ip, disassemble(ip).c_str());
			show_info(ip, rax, rbx);
			DataFile.write(buff, len);
    	}
    } 
}

/* ===================================================================== */

VOID Instruction(INS ins, VOID *v)
{
    Instruction_Info oneInstruction;
    ADDRINT ip = INS_Address(ins);
    if (ip < 0xfffffff) {
    //cz_Log(OutFile, "(-%6d)%p:%2d %s\n", count_ptr, oneInstruction.Addr, begin_to_record, oneInstruction.Instruction.c_str());
    add_to_disassemble(INS_Address(ins), INS_Disassemble(ins));
    INS_InsertCall(ins, IPOINT_BEFORE, 
                        (AFUNPTR)doStepByStep, 
                        IARG_INST_PTR, 
                        IARG_ADDRINT, INS_Size(ins), 
                        IARG_REG_VALUE, REG(REG_EAX),
                        IARG_REG_VALUE, REG(REG_EBX),
                        IARG_END);

    }
}

/* ===================================================================== */

VOID Fini(INT32 code, VOID *v)
{
    OutFile.close();
    DataFile.close();

}

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */

int main(int argc, char *argv[])
{
    if( PIN_Init(argc,argv) )
    {
        return Usage();
    }
    
    diy_init();
    INS_AddInstrumentFunction(Instruction, 0);
    PIN_AddFiniFunction(Fini, 0);

    // Never returns
    PIN_StartProgram();
    
    return 0;
}

/* ===================================================================== */
/* eof */
/* ===================================================================== */
