#include "stdio.h"
int main()
{
	char input[1000];
	char total[1000];
	scanf("%s", input);
	sprintf(total, "./binary1 %s", input);
	printf("%s\n", total);
	system(total);
	return 0;
}