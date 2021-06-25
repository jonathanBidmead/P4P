using KVBInterface;
using System;
namespace Reading
{
    public class testClass
    {
        KVPInterface KVP = new KVPInterface();
        

        private void KVPConnect()//attempts to connect, retries every 2s until success
        {
            string IP = "10.104.117.1";
            int port = 7000;
            bool success;

            do
            {
                success = KVP.Connect(IP, port, 1000);
                Console.WriteLine(success);
                System.Threading.Thread.Sleep(2000);
            } while (!success);
            
        }
        private KVPInterface.ReadResult GetReadResult(string varName)
        {
            
            return KVP.ReadVariable(varName);
        }

        public void run()
        {
            KVPConnect();
            Console.ReadKey();
            while (true) {
                string varName = "$POS_ACT";
                KVPInterface.ReadResult result = GetReadResult(varName);
                Console.WriteLine(result.value);
                System.Threading.Thread.Sleep(100);
            }
            //Console.ReadKey();

        }
    }
    
}