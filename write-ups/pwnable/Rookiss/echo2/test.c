#include<stdio.h>
int main()
{
	system("echo ${PATH:0:1}bin${PATH:0:1}ls");
	return 0;
}