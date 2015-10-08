#include <stdio.h>
#include <string.h>

int filter(char* cmd){
	int r=0;
	printf("%s\n", cmd);
	printf("%d\n", strstr(cmd, "flag"));
	printf("%d\n", strstr(cmd, "sh"));
	printf("%d\n", strstr(cmd, "tmp"));
	r += strstr(cmd, "flag")!=0;
	r += strstr(cmd, "sh")!=0;
	r += strstr(cmd, "tmp")!=0;
	printf("%d\n", r);
	return r;
}
int main(int argc, char* argv[], char** envp){
	putenv("PATH=/fuckyouverymuch");
	printf("%d\n", filter(argv[1]));
	if(filter(argv[1])) return 0;
	system( argv[1] );
	return 0;
}

