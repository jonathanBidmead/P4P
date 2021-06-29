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
                Console.ReadKey();
                
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
            string varName = "$POS_ACT";
            displayReadFromKUKA(varName);//reading current position
            KVPInterface.ReadResult output = GetReadResult(varName);
            bool step = writeToKUKA("my_step", "TRUE");
            //status = step ? "success" : "failure";
            //console.write("writing to my_step: ");
            //console.writeline(status);
            //string value = "{A1 0.0,A2 -90.0,A3 90.0,A4 0.0,A5 0.0,A6 0.0,E1 0.0,E2 0.0,E3 0.0,E4 0.0,E5 0.0,E6 0.0}";
            string val_string = String.Format("{{X {0:0.##}, Y {1:0.##}, Z {2:0.##}, A {3:0.##}, B {4:0.##}, C {5:0.##}}}", 500, 100, 0, 0, 0, 0);
            bool success = writeToKUKA("my_inc", val_string);
            Console.ReadKey();

        }
    }
}
