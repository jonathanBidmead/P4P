using System;
using KVBInterface;

namespace KVP_Writing
{
	class KUKA_Traverse
	{
        KVPInterface KVP = new KVPInterface();

        private void KVPConnect()//attempts to connect, retries every 2s until success
        {
            string IP = "10.104.117.1";
            int port = 7000;
            bool success;
            string status;

            do
            {
                Console.Write("Attempting to Connect: ");
                success = KVP.Connect(IP, port, 1000);
                status = success ? "Success" : "Failure";
                Console.WriteLine(status);
                System.Threading.Thread.Sleep(500);

            } while (!success);

        }

        private void readPosContinuous()
        {
            while (true)
            {
                string pos = KVP.ReadVariable("$POS_ACT").value;
                Console.WriteLine(pos);
                System.Threading.Thread.Sleep(500);
            }
        }
        private bool writeToKUKA(string varName, string value)
        {
            bool success = false;
            string status;
            do
            {
                Console.Write("Attempting to Write to Variable (");
                Console.Write(varName);
                Console.Write("): ");
                success = KVP.WriteVariable(varName, value);
                status = success ? "Success" : "Failure";
                Console.WriteLine(status);
                //Console.ReadKey();

            } while (!success);
            return success;
        }

        private double[] getCurrentPos()    //gets current XYZABC position and parses the string to an array of doubles
        {
            KVPInterface.ReadResult result = KVP.ReadVariable("$POS_ACT");
            string[] splitStrings = { "X ", ", Y ", ", Z ", ", A ", ", B ", ", C ", ", S" };
            string[] values = result.value.Split(splitStrings, System.StringSplitOptions.RemoveEmptyEntries);
            double[] posVals = { 0, 0, 0, 0, 0, 0 };
            //Console.WriteLine(result.value);
            for (int i = 0; i < 6; i++)
            {
                posVals[i] = Convert.ToDouble(values[i + 1]);
            }
            Console.WriteLine("Initial Position:");
            foreach (var val in posVals)
            {
                Console.WriteLine(val);
            }
            return posVals;
        }

        private void moveDirect(double[] point)
        {
            double[] initialPos = getCurrentPos();//getting robot position before move
            double[] point_rel = { 0, 0, 0, 0, 0, 0 };
            for (int i = 0; i < 6; i++)
            {
                point_rel[i] = point[i] - initialPos[i];//translating absolute to relative coordinate system
            }

            Console.WriteLine("Moving Now.");
            bool readyForNextInput = (KVP.ReadVariable("my_step").value == "FALSE") ? true : false;//ready for next input if "my_step" val == "FALSE"
            if (readyForNextInput)
            {
                bool success = writeToKUKA("my_step", "TRUE");
                string val_string = String.Format("{{X {0:0.##}, Y {1:0.##}, Z {2:0.##}, A {3:0.##}, B {4:0.##}, C {5:0.##}}}", point_rel[0], point_rel[1], point_rel[2], point_rel[3], point_rel[4], point_rel[5]);
                success = writeToKUKA("my_inc", val_string);
            }
        }
        public void run(double[] pointA_in, double[] pointB_in)
        {
            //Establish Robot Connection
            KVPConnect();
            //get robot position before move
            

            //define ptA, ptB relative to current robot position
            //double[] pointA_rel = { 0, 0, 0, 0, 0, 0 };
            //double[] pointB_rel = { 0, 0, 0, 0, 0, 0 };
            //for (int i = 0; i < 6; i++)
            //{
            //    pointA_rel[i] = pointA_in[i] - initialPos[i];
            //    pointB_rel[i] = pointB_in[i] - initialPos[i];
            //}
            //Console.WriteLine("Relative Positions Found");
            //foreach (var val in pointA_rel)
            //{
            //    Console.WriteLine(val);
            //}
            Console.ReadKey();
            //got to first point (A)
            moveDirect(pointA_in);
            //readPosContinuous();
            Console.ReadKey();
            moveDirect(pointB_in);
            Console.ReadKey();
        }
    }
}
