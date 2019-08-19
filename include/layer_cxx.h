#include<iostream> 
#include <stdio.h>
#include <math.h>
  
using namespace std; 

void   innerFill(float innerHgt[],short innerOut[],int b1_scalar,int b2_scalar);
void binHeight(int h_slice[],float binsOut[],int h_size);

void fillData(int b1[][5],int b2[][5],int hgt[][125],short output[][125],int b1_n,int fill_value)
{

	int start = 0;
	int end   = b1_n - 1; 

    float hgtBins[125];

	while(start <= end)
	{

		for(int j = 0; j <= 5 - 1; j++)
		{
            if(b1[start][j] != fill_value and b2[start][j] != fill_value)
            {
                binHeight(hgt[start],hgtBins,125);
                innerFill(hgtBins,output[start],b1[start][j],b2[start][j]);
            }
            //if(b1[end][j] != fill_value and b2[end][j] != fill_value)
            //{
            //  innerFill(binHeight(hgt[end],125),output[end],b2[end][j],b2[end][j]);
            //}
            //cout << endl;
		}

		start += 1;
		//end   -= 1;
	}
}

void innerFill(float innerHgt[],short innerOut[], int b1_scalar,int b2_scalar)
{
    // Python eqv: tmp_dtd = top_bottom_indc(hgt_bins,tmpB1[ii],tmpB2[ii])
    short new_fill = 1;

    int i = 125 - 1;
    int breakFlag = 1;
    int ind1 = -99;
    int ind2 = -99;

    while(i > 0 and breakFlag == 1)
    {
        if((float) b1_scalar >= innerHgt[i] and (float) b1_scalar < innerHgt[i - 1])
        {
            ind1 = i;
        }
        if((float) b2_scalar >= innerHgt[i] and (float) b2_scalar < innerHgt[i - 1])
        {
            ind2 = i;
        }

        if(ind1 != -99 and ind2 != -99 and ind1 > ind2)
        {
            breakFlag = 0;
            for(int ii = ind2; ii <= ind1; ii++)
            {
                innerOut[ii] = new_fill;
                //set binary array bin equal to new fill
            }
        }
        else if(ind1 != -99 and ind2 != -99 and ind1 < ind2)
        {
            breakFlag = 0;
            for(int ii = ind1; ii <= ind2; ii++)
            {
                innerOut[ii] = new_fill;
                //set binary array bin equal to new fill
            }
            //cout << endl;
        }
        else if(ind1 != -99 and ind2 != -99 and ind1 == ind2)
        {
            breakFlag = 0;
            innerOut[ind1] = new_fill;
            //printf("%d%10d\n",ind1,ind2);
        }

        i -= 1;
    }
}

void binHeight(int h_slice[],float binsOut[],int h_size)
{
    float heightRes = fabs((float) h_slice[0] - (float) h_slice[1]) / 2.;

    for(int i = 0; i <= 125 - 1; i++)
    {
        binsOut[i] = ((float) h_slice[i]) - heightRes;
        //printf("%d%10.1f\n",h_slice[i],binsOut[i]);
    }
    //exit(1);

}
