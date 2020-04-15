// File name: /XVMTc/Test.tst

load XVMTc.asm,
output-file test.out,
//compare-to test.cmp,

//Set RAM[TEST] and RAM[TEST-1] to different values
//set PC 0,
//set RAM[2999] 0,
//set RAM[3000] 0;

//=============================================================
// Run the preample code and capture the start time
//=============================================================
output-list time%S1.16.1,
while RAM[3000] =  RAM[2999] {ticktock,} 
output;
//=============================================================

//=============================================================
// DATA PASSES
//=============================================================
output-list RAM[3000]%D1.7.1
RAM[3001]%D1.7.1 RAM[3002]%D1.7.1 RAM[3003]%D1.7.1 RAM[3004]%D1.7.1
RAM[3005]%D1.7.1 RAM[3006]%D1.7.1 RAM[3007]%D1.7.1 RAM[3008]%D1.7.1,

while RAM[3000] <> RAM[2999] {ticktock,} while RAM[3000] = RAM[2999] {ticktock,} output;  
while RAM[3000] <> RAM[2999] {ticktock,} while RAM[3000] = RAM[2999] {ticktock,} output;  
while RAM[3000] <> RAM[2999] {ticktock,} while RAM[3000] = RAM[2999] {ticktock,} output;  
while RAM[3000] <> RAM[2999] {ticktock,} while RAM[3000] = RAM[2999] {ticktock,} output;  
//=============================================================

//=============================================================
// Run the postamble code and capture the stop flag.
//=============================================================
output-list time%S1.16.1 RAM[3001]%D1.7.1,
while RAM[3000] <> RAM[2999] {ticktock,} while RAM[3000] = RAM[2999] {ticktock,} output;  
//=============================================================
