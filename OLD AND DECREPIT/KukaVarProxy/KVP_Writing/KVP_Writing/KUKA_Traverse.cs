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
        public void run()
        {

        }
    }
}
