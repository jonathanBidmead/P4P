using System;
namespace KVP_Writing
{
	static class Program
	{
		static void Main()
		{
			KUKA_Write write = new KUKA_Write();
			write.run();
		}
	}
}
