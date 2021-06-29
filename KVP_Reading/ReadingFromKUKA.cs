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
            string status;

            do
            {
                Console.Write("Attempting to Connect: ");
                success = KVP.Connect(IP, port, 1000);
                status = success ? "Success" : "Failure";
                Console.WriteLine(status);
                System.Threading.Thread.Sleep(200);

            } while (!success);
            
        }
        private KVPInterface.ReadResult GetReadResult(string varName)
        {
            
            return KVP.ReadVariable(varName);
        }

        private void readFromKUKA(string varName)
        {
            Console.Write("Reading Variable: ");
            Console.Write(varName);
            Console.Write(" Value: ");
            KVPInterface.ReadResult result = GetReadResult(varName);
            Console.WriteLine(result.value);
        }
        public void run()
        {
            KVPConnect();
            Console.WriteLine("Awaiting User Confirmation (keypress)");
            Console.ReadKey();
            while (true) {
                readFromKUKA("my_rel");
                System.Threading.Thread.Sleep(500);
            }
            //Console.ReadKey();

        }
    }
    
}