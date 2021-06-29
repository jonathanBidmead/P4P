using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using KVBInterface;

namespace KVP_Writing
{
    class KUKA_Write
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
                System.Threading.Thread.Sleep(2000);

            } while (!success);

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

        private void displayReadFromKUKA(string varName)
        {
            Console.Write("Reading Variable: ");
            Console.Write(varName);
            Console.Write(" Value: ");
            KVPInterface.ReadResult result = GetReadResult(varName);
            Console.WriteLine(result.value);
        }

        private KVPInterface.ReadResult GetReadResult(string varName)
        {

            return KVP.ReadVariable(varName);
        }

        public void run()
        {
            KVPConnect();
            Console.WriteLine("Connected, Awaiting User Confirmation (keypress)");
            Console.ReadKey();
            string status;
            bool step = writeToKUKA("my_step", "TRUE");
            Console.WriteLine("Start?:");
            string input = Console.ReadLine();
            string val_string = "";
            bool success = false;
            //System.Threading.Thread.Sleep(3000);
            //val_string = String.Format("{{X {0:0.##}, Y {1:0.##}, Z {2:0.##}, A {3:0.##}, B {4:0.##}, C {5:0.##}}}", 0, 0, 0, 0, 0, 0);
            //success = writeToKUKA("my_inc", val_string);
            //while(input != "q")
            //{
            //    Console.WriteLine("Enter x:");
            //    input = Console.ReadLine();
            //    string val_string = String.Format("{{X {0:0.##}, Y {1:0.##}, Z {2:0.##}, A {3:0.##}, B {4:0.##}, C {5:0.##}}}", 0, 0, Int16.Parse(input), 0, 0, 0);
            //    bool success = writeToKUKA("my_inc", val_string);
            //    System.Threading.Thread.Sleep(500);
            //    val_string = String.Format("{{X {0:0.##}, Y {1:0.##}, Z {2:0.##}, A {3:0.##}, B {4:0.##}, C {5:0.##}}}", 0, 0, 0, 0, 0, 0);
            //    success = writeToKUKA("my_inc", val_string);

            //}
            int[] X = new int[] { 10, 0, -10, 0, 10, 0, -10, 0, 10, 0 };
            int[] Y = new int[] { 0, 10, 0, -10, 0, 10, 0, -10, 0, 0 };
            int scale = 8;
            for (int i = 0; i < 10; i++)
            {
                success = writeToKUKA("my_step", "TRUE");
                val_string = String.Format("{{X {0:0.##}, Y {1:0.##}, Z {2:0.##}, A {3:0.##}, B {4:0.##}, C {5:0.##}}}", scale*X[i], scale*Y[i], 0, 0, 0, 0);
                success = writeToKUKA("my_inc", val_string);
                System.Threading.Thread.Sleep(500);
            }
            Console.ReadKey();

        }
    }
}
