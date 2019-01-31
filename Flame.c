#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

int main(int argc, char** argv)
{

  double rad, deg, min, sec;
  
  
  sscanf(argv[1],"%lf", &deg);
  sscanf(argv[2],"%lf", &min);
  sscanf(argv[3],"%lf", &sec);
  

  while(1)
    {

      rad = (M_PI)*((deg+(min/60)+(sec/3600))/180);
  
      printf("Radianos: %lf\nNovo valor: ", rad);

      scanf("%lf %lf %lf", &deg, &min, &sec);
      
    }
  return 0;
}
