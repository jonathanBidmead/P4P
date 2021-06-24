using System;
using System.Collections.Generic;
using System.Text;

namespace RobVisKUKA
{
    public class RobVar
    {
        public string Name;
        public string Type;
        public string Value;
        public int EnabledMode;
        public int AutoSendTime;
        public double AutoSendValue;
        public double elapsedtime;
        public double elapsedvalue;

        public RobVar(string name)
        {
            Name = name;
            Type = "numeric";
            Value = "0";
            EnabledMode = 0;
            AutoSendTime = 2000; //every 2 seconds
            AutoSendValue = 0.05; //every absolute change of 1
            elapsedtime = 0;
            elapsedvalue = 0;
           
        }
    }   
}
