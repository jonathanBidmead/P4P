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
            string IP = "10.104.117.2";
            int port = 7000;
            bool success;

            do
            {
                success = KVP.Connect(IP, port, 1000);
                Console.WriteLine(success);
                System.Threading.Thread.Sleep(2000);
            } while (!success);

        }

        private bool writeToKUKA(string value)
        {
            string pVarName = "$OUT[1]";
            bool success = KVP.WriteVariable(pVarName, value);
            return success;
        }

        public void run()
        {
            KVPConnect();
            Console.ReadKey();
            string value = "TRUE";
            bool success = writeToKUKA(value);
            Console.WriteLine(success);
            Console.ReadKey();

        }
    }
}
