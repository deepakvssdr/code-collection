#include<stdio.h>
#include<stdlib.h>
int n,rem,a[10],t=-1,i;
void push(int m);
void pop();  



void main()
{
    printf("Enter size:");
    scanf("%d",&n);
    push(n);
    printf("Reversed Number: ");
     pop();
}/*main()*/

void push(int m)
{
    printf("Enter numbers:");
    for(i=0;i<m;i++)
        scanf("%d",&a[++t]);
}/*push()*/

void pop()
{
    while (t!=-1) 
        printf("%d ",a[t--]);
}/*pop()*/