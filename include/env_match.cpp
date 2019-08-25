#include<iostream> 
#include <stdio.h>
#include <math.h>
#include <vector>
  
using namespace std; 

const int missing = -99;

void match_lat_coords(float bounds[2],float bins[],int output[2],int n);
void match_lon_coords(float bounds[2],float bins[],int output[2],int n);

void match_env(float lat_bnds[][2], float lon_bnds[][2], float lat_bins[], float lon_bins[], int num_clds, int num_lat_bins, int num_lon_bins)
{
    int out_lat_indices[2];
    int out_lon_indices[2];

    out_lat_indices[0] = missing; out_lat_indices[1] = missing;

    out_lon_indices[0] = missing;
    out_lon_indices[1] = missing;

    for(int i = 0; i < num_clds; i++)
    {
        //match_lat_coords(lat_bnds[i],lat_bins,out_lat_indices,num_lat_bins);
        match_lon_coords(lon_bnds[i],lon_bins,out_lon_indices,num_lon_bins);
        //printf("%.2f%10.2f\n",lon_bins[out_lon_indices[0]],lon_bins[out_lon_indices[1]]);
    }
}

void match_lat_coords(float bounds[2],float bins[],int output[2],int n)
{
    //int missing = -99;
    int end   = n - 1;
    int start = 0;
    int ind1  = missing;
    int ind2  = missing;

    int breakFlag = 1;

    while(end > start and breakFlag == 1)
    {
        //printf("%.2f%10.2f%10.2f\n",bins[end],bounds[0],bins[end - 1]);
        if(bounds[0] >= bins[end] and bounds[0] < bins[end - 1])
        {
            ind1 = end;
        }
        if(bounds[1] >= bins[end] and bounds[1] < bins[end - 1])
        {
            ind2 = end;
        }

        if(ind1 != missing and ind2 != missing)
        {
            breakFlag = 0;
        }

        end -= 1;
    }

    if(ind1 == missing or ind2 == missing)
    {
        throw ind1;
    }

    if(ind1 < ind2)
    {
        output[0] = ind1;
        output[1] = ind2;
    } else if(ind2 < ind1){
        output[0] = ind2;
        output[1] = ind1;
    } else{
        output[0] = ind1;
        output[1] = ind1;
    }
    
}

void match_lon_coords(float bounds[2],float bins[],int output[2],int n)
{
    //int missing = -99;
    int end   = n - 1;
    int i     = end;
    int start = 0;
    int ind1  = missing;
    int ind2  = missing;

    int breakFlag = 1;

    while(i > start and breakFlag == 1)
    {
        //printf("%.2f%10.2f%10.2f\n",bins[end],bounds[0],bins[end - 1]);
        if(bounds[0] >= bins[i] and bounds[0] < bins[i - 1])
        {
            ind1 = i;
        }
        if(bounds[1] >= bins[i] and bounds[1] < bins[i - 1])
        {
            ind2 = i;
        }

        if(ind1 != missing and ind2 != missing)
        {
            breakFlag = 0;
        }

        i -= 1;
    }

    if(ind1 == missing and ind2 == missing)
    {
        if(bounds[0] > bins[start] and bounds[1] > bins[start])
        {
            ind1 = start;
            ind2 = start;
        }else if(bounds[0] < bins[end] and bounds[1] < bins[end]){
            ind1 = end;
            ind2 = end;
        }else{
            try{
                throw 20;
            }catch(int e){
                cout << "another condition is needed to address both lon bin bounds being missing" << endl;
            }
        }
    }else if(ind1 != missing and ind2 == missing){
        if(bounds[1] > bins[start])
        {
            ind2 = start;
        }else if(bounds[1] < bins[end]){
            ind2 = end;
        }
    }else if(ind1 == missing and ind2 != missing){
        if(bounds[0] > bins[start])
        {
            ind1 = start;
        }else if(bounds[0] < bins[end]){
            ind1 = end;
        }
    }

    if(ind1 < ind2)
    {
        output[0] = ind1;
        output[1] = ind2;
    } else if(ind2 < ind1){
        output[0] = ind2;
        output[1] = ind1;
    } else{
        output[0] = ind1;
        output[1] = ind1;
    }
    cout << output[1] - output[0] << endl;
    
}
