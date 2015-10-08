#include<stdio.h>
int main(int argc, char const *argv[])
{
	unsigned long long a, b, c, d, e, f, g;
	a = 10;
	b = 20;
	c = 11111111111111111111;
	d = 11938883622100703890;
	e = 11111111111111111111;
	f = 60;
	g = 70;
	//printf("%4$llu\n", a, b, c, d, e, f, g);
	printf("a = %llu, b = %llu, c = %llu, d = %llu, e = %llu, f = %llu, g = %llu\n", a, b, c, d, e, f, g);
	if (argc > 1) {
		char format[100];
		//ln=8, n=4,hn=2,hhn=1 
		sprintf(format, "%%3$llu,%%4$%s\n", argv[1]);
		printf(format, a, b, c, &d, e, f, g);
	}
	else
		printf("%3$llu,%4$hn\n", a, b, c, &d, e, f, g);

	printf("a = %llu, b = %llu, c = %llu, d = %llu, e = %llu, f = %llu, g = %llu\n", a, b, c, d, e, f, g);
	return 0;
}