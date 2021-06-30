using System;
namespace KVP_Writing
{
	static class Program
	{
		static void Main()
		{
            KUKA_Write write = new KUKA_Write();
            write.run();
            //KUKA_Traverse move = new KUKA_Traverse();
            //         double[] pointA = { 260, -490, 1270, -107, 90, -17 };
            //         //double[] pointA = { 0, 150, 0, 0, 0, 0 };//debug: this is already relative to the tool
            //         double[] pointB = { -275,-700,1400,110,90,-180 };
            //move.run(pointA, pointB);
        }
	}
}
