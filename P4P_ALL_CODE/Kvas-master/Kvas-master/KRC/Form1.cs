using KVBInterface;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Data.SqlTypes;
using System.Drawing;
using System.Drawing.Text;
using System.IO;
using System.IO.Ports;
//using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading;
//using System.Threading.Tasks;
using System.Windows.Forms;
using System.Xml.Serialization;
using System.Runtime.InteropServices;


namespace RobVisKUKA
{
    public partial class Form1 : Form
    {
        SerialPort Serial = new SerialPort();
        KVPInterface KVP = new KVPInterface();
        List<RobVar> Variables = new List<RobVar>();
        bool debugflag = false;
        bool ToKVPAvailable = false;
        bool ToSerialAvailable = false;
        byte[] totalbuffer = new Byte[36]; //why tf did I leave this one at 32, and why did it not trigger before? Ah. because it was only sending so far
        private int buffcount = 0;

        private bool debug_flag = false;
        private bool debug_heartbeat = false;

        string ROBOT_NAME = "KR10";

        public struct KvasPos
        {
            public float command, v1, v2, v3, v4, v5, v6, v7, chksum;

            public KvasPos(byte[] buffer)
            {

                float[] vals = new float[buffer.Length / 4];
                for (int i = 0; i < vals.Length; i++)
                {
                    if (BitConverter.IsLittleEndian)
                    {
                        // Array.Reverse(buffer, i * 4, 4);
                    }
                    vals[i] = BitConverter.ToSingle(buffer, i * 4);

                }
                //if (vals.Length != 8)
                //    throw new ArgumentException();
                command = vals[0];
                v1 = vals[1];
                v2 = vals[2];
                v3 = vals[3];
                v4 = vals[4];
                v5 = vals[5];
                v6 = vals[6];
                v7 = vals[7];
                chksum = vals[8];
            }

            public KvasPos(int arg_command, float[] vals)
            {

                command = arg_command;
                v1 = vals[0];
                v2 = vals[1];
                v3 = vals[2];
                v4 = vals[3];
                v5 = vals[4];
                v6 = vals[5];
                v7 = vals[6];
                chksum = v1 + v2 + v3 + v4 + v5 + v6 + v7;
            }

            public KvasPos(int arg_command, byte[] buffer)
            {

                float[] vals = new float[buffer.Length / 4];
                for (int i = 0; i < vals.Length; i++)
                {
                    if (BitConverter.IsLittleEndian)
                    {
                        Array.Reverse(buffer, i * 4, 4);
                    }
                    vals[i] = BitConverter.ToSingle(buffer, i * 4);
                }
                //if (vals.Length != 8)
                //    throw new ArgumentException();
                command = arg_command;
                v1 = vals[0];
                v2 = vals[1];
                v3 = vals[2];
                v4 = vals[3];
                v5 = vals[4];
                v6 = vals[5];
                v7 = vals[6];
                chksum = v1 + v2 + v3 + v4 + v5 + v6 + v7;
            }

            public byte[] toByteArray()
            {
                int size = Marshal.SizeOf(this);
                byte[] arr = new byte[size];

                IntPtr ptr = Marshal.AllocHGlobal(size);
                Marshal.StructureToPtr(this, ptr, true);
                Marshal.Copy(ptr, arr, 0, size);
                Marshal.FreeHGlobal(ptr);
                return arr;
            }

            public int sizeByteArray()
            {
                return (4 * 8);
            }
        }

        private KvasPos rx_mqtt;
        private Boolean onlySerial = false;

        public bool BridgeOpen { get; private set; }

        public Form1()
        {
            InitializeComponent();

            //Info
            PrintInfo();

            //Main
            ConfigValues();
            timer1.Enabled = true;
            //timer2.Enabled = true;
            AddAxesVar();

            //For debug
            if (debug_flag)
            {

                Serial.DataReceived += Serial_DataReceived_New;
            }

        }

        private void Test()
        {
            return;
            KvasPos testpos = new KvasPos();
            testpos.command = 999999999;
            testpos.v1 = 1;
            testpos.v2 = 2;
            testpos.v3 = 3;
            testpos.v4 = 4;
            testpos.v5 = 5;
            testpos.v6 = 6;
            testpos.chksum = 69;
            //var buffer = testpos.toByteArray();
            Serial.Write(testpos.toByteArray(), 0, testpos.sizeByteArray());
            //Serial.WriteLine("1234567891113151719212325272931");
            //Serial.BreakState = true;
            //Serial.BreakState = false;
        }
        private void timer1_Tick(object sender, EventArgs e)
        {
            if (debug_heartbeat)
            {
                AppendText("1.");
            }
            if (!KVP.Connected)
            {
                timer2.Enabled = false;
                this.BridgeOpen = false;
                ConnectKVP();
            }
            if (!Serial.IsOpen)
            {
                timer2.Enabled = false;
                this.BridgeOpen = false;
                OpenSerial();
            }
            else
            {
                //this.onlySerial = true;
                //timer2.Enabled = true;
            }

            //if (KVP.Connected && Serial.IsOpen && !BridgeOpen)
            if (true && Serial.IsOpen && !BridgeOpen)

                {
                    LinkEvents();
                this.BridgeOpen = true;
                timer2.Enabled = true;
            }

            //timer2.Enabled = true;

        }

        private void LinkEvents()
        {
            Serial.DataReceived -= Serial_DataReceived_New;
            Serial.DataReceived += Serial_DataReceived_New;

            textBox1.AppendText("Bridge established/n");

        }
        delegate void SetTextCallback(string text);

        private void AppendText(string text)
        {
            // InvokeRequired required compares the thread ID of the
            // calling thread to the thread ID of the creating thread.
            // If these threads are different, it returns true.
            if (this.textBox1.InvokeRequired)
            {
                SetTextCallback d = new SetTextCallback(AppendText);
                this.Invoke(d, new object[] { text });
            }
            else
            {
                this.textBox1.AppendText(text);
            }
        }
        private void Serial_DataReceived_New(object sender, SerialDataReceivedEventArgs e)
        {
            if (debug_heartbeat)
            {
                AppendText("S.");
            }
            //return;
            if (debug_flag)
            {

                AppendText("Serial received:");
            }
            try
            {
                bool serialok = false;
                while (Serial.BytesToRead > 0)
                {
                    byte thebyte = (byte)Serial.ReadByte();
                    if (debug_flag)
                    {

                        AppendText(thebyte.ToString());
                        AppendText(":");
                    }
                    if ((thebyte == '\n'))
                    {
                        if (buffcount == 0)
                        {
                            serialok = true;
                            buffcount = 0;
                            break;
                        }
                    }
                    totalbuffer[buffcount] = thebyte;
                    buffcount++;
                    if ((buffcount >= 36))
                    {
                        buffcount = 0;
                    }
                }

                if (serialok)
                {
                    //textBox1.AppendText("Got stuff with newline");
                    rx_mqtt = new KvasPos(totalbuffer);
                    if (debug_flag)
                    {
                        AppendText("\n");
                        AppendText("Parsed data:\n");
                        AppendText((rx_mqtt.v1.ToString()));
                        AppendText("\n");
                        AppendText((rx_mqtt.v2.ToString()));
                        AppendText("\n");
                        AppendText((rx_mqtt.v3.ToString()));
                        AppendText("\n");
                        AppendText((rx_mqtt.v4.ToString()));
                        AppendText("\n");
                        AppendText((rx_mqtt.v5.ToString()));
                        AppendText("\n");
                        AppendText((rx_mqtt.v6.ToString()));
                        AppendText("\n");
                        AppendText((rx_mqtt.v7.ToString()));
                    }

                    ToKVPAvailable = true;

                }

                buffcount = 0;
            }
            catch (IOException exc)
            {
                //handleAppSerialError(exc);
            }
        }


        private void Serial_DataReceived(object sender, SerialDataReceivedEventArgs e)
        {
            try
            {
                string line = Serial.ReadLine();

                var splits = line.Split('/');
                var value = splits[splits.Length - 1];
                string varname = "";
                string varproperty = "";
                string varmode = "Get";


                string othername = "";
                string othercommand = "";

                for (int i = 0; i < splits.Length - 2; i++)
                {
                    if (splits[i] == "Vars")
                    {
                        varname = splits[i + 1];
                        varproperty = splits[i + 2];
                        if (splits.Length >= i + 2)
                        {
                            varmode = splits[i + 3];
                        }
                        ProcessVarCommand(varname, varproperty, varmode, value);
                        break;
                    }
                    if (splits[i] == "Conf")
                    {
                        varname = splits[i + 1];
                        varproperty = splits[i + 2];
                        ProcessOtherCommand(othername, othercommand, value);
                        break;
                    }
                }




                return;

                //Checksum first
                if (splits.Length == 4)
                {
                    if (splits[2] == "C")
                    {
                        //CalcCheckSum(splits);
                        var checksumsend = (byte)(splits[3].ToCharArray()[0]);
                        if (splits[0] == "Q")
                        {
                            var result = KVP.ReadVariable(splits[1]);
                            if (result.readOk)
                            {
                                string retstring = "R:{0}:C:0";
                                if (Serial.IsOpen)
                                {
                                    Serial.WriteLine(string.Format(retstring, result.value));
                                }
                            }
                        }
                    }
                }

            }
            catch (TimeoutException)
            {

                // throw;
            }

            //throw new NotImplementedException();
        }

        private void ProcessOtherCommand(string othername, string othercommand, string value)
        {
            //throw new NotImplementedException();
        }

        private void ProcessVarCommand(string varname, string property, string mode, string value)
        {
            //Check first if variable contained
            if (Variables.Exists(x => x.Name.Equals(varname, StringComparison.OrdinalIgnoreCase)))
            {
                if (property.Equals("Delete", StringComparison.OrdinalIgnoreCase) && varname.Equals(value, StringComparison.OrdinalIgnoreCase))
                {
                    Variables.RemoveAll(x => x.Name.Equals(varname, StringComparison.OrdinalIgnoreCase));
                }
                else
                {
                    var currentvar = Variables.Find(x => x.Name.Equals(varname, StringComparison.OrdinalIgnoreCase));

                    switch (property)
                    {
                        case "Val":
                            if (mode.Equals("Set", StringComparison.OrdinalIgnoreCase))
                            {
                                currentvar.Value = value;
                                var result = KVP.WriteVariable(varname, currentvar.Value);
                            }
                            else
                            {
                                //Get the variable first
                                var result = KVP.ReadVariable(varname);
                                if (result != null && result.readOk)
                                {
                                    currentvar.Value = result.value;
                                    SendVarProperty(varname, "Val", currentvar.Value);
                                }
                            }
                            break;
                        case "EnabledMode":
                            if (mode.Equals("Set", StringComparison.OrdinalIgnoreCase))
                            {
                                int ival;
                                var result = int.TryParse(value, out ival);
                                if (result) currentvar.EnabledMode = ival;
                            }
                            else
                            {
                                SendVarProperty(currentvar.Name, "EnabledMode", currentvar.EnabledMode);
                            }
                            break;
                        case "AutoSendTime":
                            if (mode.Equals("Set", StringComparison.OrdinalIgnoreCase))
                            {
                                int ival;
                                var result = int.TryParse(value, out ival);
                                if (result) currentvar.AutoSendTime = ival;
                            }
                            else
                            {
                                SendVarProperty(currentvar.Name, "AutoSendTime", currentvar.AutoSendTime);
                            }
                            break;
                        case "AutoSendValue":
                            if (mode.Equals("Set", StringComparison.OrdinalIgnoreCase))
                            {
                                int ival;
                                var result = int.TryParse(value, out ival);
                                if (result) currentvar.AutoSendValue = ival;
                            }
                            else
                            {
                                SendVarProperty(currentvar.Name, "AutoSendValue", currentvar.AutoSendValue);
                            }
                            break;
                        default:
                            break;
                    }
                }
            }
            else
            {
                if (property.Equals("Create", StringComparison.OrdinalIgnoreCase) && varname.Equals(value, StringComparison.OrdinalIgnoreCase))
                {
                    Variables.Add(new RobVar(value));
                }
            }


        }

        private void SendVarProperty(string varname, string property, double autoSendValue)
        {
            SendVarProperty(varname, property, autoSendValue.ToString());
        }

        private void SendVarProperty(string varname, string property, int enabledMode)
        {
            SendVarProperty(varname, property, enabledMode.ToString());
        }

        private void SendVarProperty(string varname, string property, string value)
        {


            string basetopic = "RV/Vars/";
            string topic = basetopic + varname + "/" + property + "/Is/" + value;
            if (debugflag)
            {
                textBox1.AppendText("Serial write: ");
                textBox1.AppendText(topic + "\n");
            }
            try
            {
                Serial.WriteLine(topic);
            }
            catch (TimeoutException)
            {
                textBox1.AppendText("Serial Timeout, message: " + topic + "\n");
            }
        }

        private void OpenSerial()
        {
            string commessage = "Opening COM-Port {0} with {1} Baud..\n";
            textBox1.AppendText(string.Format(commessage, Serial.PortName, Serial.BaudRate));
            try
            {
                Serial.Open();
            }
            catch (Exception ex)
            {
                textBox1.AppendText(ex.Message + "\n");
                // throw;
            }


            if ((bool)Serial.IsOpen == true)
            {
                textBox1.AppendText("Openend sucessfully\n");
            }
            else
            {
                textBox1.AppendText("Could not open. Reattempting..\n");
            }
        }


        private void ConnectKVP()
        {


            string kvpmessage = "Connecting to KUKAVarProxy at {0}:{1}..\n";
            textBox1.AppendText(string.Format(kvpmessage, KVP.IP, KVP.Port));
            var KVPresult = KVP.Connect();
            if ((bool)KVPresult == true)
            {
                textBox1.AppendText("Connected sucessfully\n");
            }
            else
            {
                textBox1.AppendText("Could not connect. Reattempting..\n");
            }
        }


        private void ConfigValues()
        {

            textBox1.AppendText("Starting with default values.\n");
            KVP.IP = "10.104.117.2";
            KVP.Port = 7000;
            KVP.timeout = 100;

            if (ROBOT_NAME == "KR10")
            {
                Serial.PortName = "COM3";

            }
            else
            {
                Serial.PortName = "COM2";

            }
            //Serial.Handshake = Handshake.XOnXOff;
            Serial.BaudRate = 115200;
            Serial.ReadTimeout = 1000;
            Serial.WriteTimeout = 1000;
            Serial.WriteBufferSize = 36; //used to be 32... anyreason?

            return;

            textBox1.AppendText("/n");
            textBox1.AppendText("Manual configuration");
            textBox1.AppendText("IP to connect to? (default: 127.0.0.1)");

        }



        private void PrintInfo()
        {
            textBox1.AppendText("KUKAVarProxy to Serial Bridge\n");

            string fmtStd = "Version: {0}.{1}.{2} \n";
            Version std = Assembly.GetExecutingAssembly().GetName().Version;
            textBox1.AppendText(String.Format(fmtStd, std.Major, std.Minor, std.Build));

            //var linkTimeLocal = //Assembly.GetExecutingAssembly().GetLinkerTime();
            DateTime linkTimeLocal = File.GetLastWriteTime(Application.ExecutablePath);
            textBox1.AppendText("Builddate " + linkTimeLocal.ToShortDateString());
            textBox1.AppendText(" Buildnumber " + std.Revision.ToString() + "\n");

            textBox1.AppendText("David Tomzik - University of Auckland\n");
            textBox1.AppendText("=========================================\n");
            textBox1.AppendText("\n");

        }

        float process_split(string split)
        {
            var snip = split.TrimEnd(',');
            float retval = 0;
            float.TryParse(snip, out retval);
            return retval;


        }

        private void timer2_Tick(object sender, EventArgs e)
        {
            if (debug_heartbeat)
            {
                AppendText("2.");
            }
            try
            {
                if (this.onlySerial)
                {
                    byte[] test = new byte[128];
                    test[0] = (byte)'A';
                    test[1] = 2;
                    test[2] = 3;
                    test[3] = 4;
                    test[4] = 5;
                    test[5] = 6;
                    test[6] = 7;
                    test[7] = 8;
                    test[8] = 9;
                    test[32] = 10;
                    textBox1.AppendText("buffer state: ");

                    Serial.Write(test, 0, 32);
                    Serial.Write(test, 0, 1);

                    //Serial.WriteLine()


                    //Serial.Write(test, 0, 32);

                    //Serial.Write(test, 0, 32);

                    //Serial.BaseStream.Flush();
                    //Serial.Write(test, 0, 32);

                    //Serial.Write(test, 0, 32);
                    //Serial.WriteLine("Du Hurensohn");
                    //Serial.BaseStream.Flush();


                    textBox1.AppendText(Serial.BytesToWrite.ToString());
                    textBox1.AppendText("\n");

                    return;
                }

                //Get from KVP and send it off via Serial
                if(true)
                { 
                var kvp_result = KVP.ReadVariable("$AXIS_ACT");
                if (kvp_result != null)
                {
                    if (kvp_result.readOk)
                    {
                        string[] splits = kvp_result.value.Split(' ');
                        if (debugflag)
                        {
                            textBox1.AppendText("KVP raw: \n");
                            textBox1.AppendText(kvp_result.value);
                            textBox1.AppendText("\n");

                            textBox1.AppendText("stringsplit read: \n");
                            foreach (var item in splits)
                            {
                                textBox1.AppendText(item.ToString());
                                textBox1.AppendText("\n");
                            }
                        }

                        float[] floatarray = new float[7];
                        floatarray[0] = process_split(splits[2]);
                        floatarray[1] = process_split(splits[4]);
                        floatarray[2] = process_split(splits[6]);
                        floatarray[3] = process_split(splits[8]);
                        floatarray[4] = process_split(splits[10]);
                        floatarray[5] = process_split(splits[12]);
                        floatarray[6] = 0;
                        if (14 < splits.Length)
                        {
                            floatarray[6] = process_split(splits[14]);
                        }
                        if (debugflag)
                        {
                            textBox1.AppendText("parsed from KRC: \n");
                            foreach (var item in floatarray)
                            {
                                textBox1.AppendText(item.ToString());
                                textBox1.AppendText("\n");
                            }
                        }

                        KvasPos tx_uart = new KvasPos(0, floatarray);

                        var tx_buffer = tx_uart.toByteArray();

                        byte[] control_sequence = new byte[1];
                        control_sequence[0] = 10;

                        Serial.Write(tx_buffer, 0, 36);
                        Serial.Write(control_sequence, 0, control_sequence.Length);
                        //Serial.BreakState = true;
                        //Serial.BreakState = false;


                        if (debugflag)
                        {
                            //textBox1.AppendText("UART write: ");
                            textBox1.AppendText("UART write: \n");
                            foreach (var item in tx_buffer)
                            {
                                textBox1.AppendText(item.ToString());
                            }

                            textBox1.AppendText("\n");
                        }

                        //SendVarProperty(currentvar.Name, "Val", currentvar.Value);
                    }
                }
                }
                if (false)
                {
                    Thread.Sleep(2);

                    //Get from KVP and send it off via Serial
                    var kvp_result_pos = KVP.ReadVariable("$POS_ACT");
                    if (kvp_result_pos != null)
                    {
                        if (kvp_result_pos.readOk)
                        {
                            string[] splits = kvp_result_pos.value.Split(' ');
                            if (debugflag)
                            {
                                textBox1.AppendText("KVP raw: \n");
                                textBox1.AppendText(kvp_result_pos.value);
                                textBox1.AppendText("\n");

                                textBox1.AppendText("stringsplit read: \n");
                                foreach (var item in splits)
                                {
                                    textBox1.AppendText(item.ToString());
                                    textBox1.AppendText("\n");
                                }


                            }

                            float[] floatarray = new float[6];
                            floatarray[0] = process_split(splits[2]);
                            floatarray[1] = process_split(splits[4]);
                            floatarray[2] = process_split(splits[6]);
                            floatarray[3] = process_split(splits[8]);
                            floatarray[4] = process_split(splits[10]);
                            floatarray[5] = process_split(splits[12]);
                            if (debugflag)
                            {
                                textBox1.AppendText("parsed : \n");
                                foreach (var item in floatarray)
                                {
                                    textBox1.AppendText(item.ToString());
                                    textBox1.AppendText("\n");
                                }
                            }

                            KvasPos tx_uart = new KvasPos(1, floatarray);

                            var tx_buffer = tx_uart.toByteArray();

                            byte[] control_sequence = new byte[1];
                            control_sequence[0] = 10;

                            Serial.Write(tx_buffer, 0, 32);
                            Serial.Write(control_sequence, 0, control_sequence.Length);
                            //Serial.BreakState = true;
                            //Serial.BreakState = false;

                            if (debugflag)
                            {
                                //textBox1.AppendText("UART write: ");
                                textBox1.AppendText("UART write: \n");
                                foreach (var item in tx_buffer)
                                {
                                    textBox1.AppendText(item.ToString());
                                }

                                textBox1.AppendText("\n");
                            }

                            //SendVarProperty(currentvar.Name, "Val", currentvar.Value);
                        }
                    }
                }

                //Put variable from Serial run into KVP
                if (ToKVPAvailable)
                {
                    ToKVPAvailable = false;

                    var calc_chk = rx_mqtt.v1 + rx_mqtt.v2 + rx_mqtt.v3 + rx_mqtt.v4 + rx_mqtt.v5 + rx_mqtt.v6;
                    var rx_chk = rx_mqtt.chksum;

                    if (Math.Abs(calc_chk - rx_chk) > 0.01)
                    {
                        textBox1.AppendText("Checksum wrong\n");
                        textBox1.AppendText("Calc: ");
                        textBox1.AppendText(calc_chk.ToString());
                        textBox1.AppendText("Rec: ");
                        textBox1.AppendText(rx_chk.ToString());
                        return;
                    }


                    bool kvpresult = false;
                    if (rx_mqtt.command == 2)
                    {
                        kvpresult = KVP.WriteVariable("MYX", rx_mqtt.v1.ToString());
                        kvpresult = KVP.WriteVariable("MYZ", rx_mqtt.v3.ToString());

                        kvpresult = KVP.WriteVariable("MYY", rx_mqtt.v2.ToString());
                        kvpresult = KVP.WriteVariable("MYB", rx_mqtt.v5.ToString());
                    }

                    if (rx_mqtt.command == 3)
                    {
                        if(debug_flag)
                        
                        {
                            textBox1.AppendText("Sending increment and step to robot\n");
                        

                        textBox1.AppendText("Sending:");
                        textBox1.AppendText(frame_to_string(rx_mqtt));
                        }
                        kvpresult = KVP.WriteVariable("my_inc", frame_to_string(rx_mqtt));

                        if (debug_flag)
                        {
                            textBox1.AppendText("past increment\n");
                            textBox1.AppendText("KVPresult: ");
                            textBox1.AppendText(kvpresult.ToString());
                        }
                        kvpresult = KVP.WriteVariable("my_step", "True");
                        if (debug_flag)
                        {
                            textBox1.AppendText("past step\n");
                            textBox1.AppendText("KVPresult: ");
                            textBox1.AppendText(kvpresult.ToString());
                        }
                    }

                    if (rx_mqtt.command == 0)
                    {
                        // kvpresult = KVP.WriteVariable("$AXIS_ACT", BitConverter.ToString(byteArray));
                    }

                    if (debug_flag)
                    {

                        textBox1.AppendText("Parsed data:");
                        textBox1.AppendText(rx_mqtt.v1.ToString());
                        textBox1.AppendText(rx_mqtt.v2.ToString());
                        textBox1.AppendText(rx_mqtt.v3.ToString());
                        textBox1.AppendText(rx_mqtt.v4.ToString());
                        textBox1.AppendText(rx_mqtt.v5.ToString());
                        textBox1.AppendText(rx_mqtt.v6.ToString());
                    }
                }

                return;

                for (int i = 0; i < Variables.Count; i++)
                {
                    var currentvar = Variables[i];
                    currentvar.elapsedtime += timer2.Interval;
                    if (currentvar.elapsedtime > currentvar.AutoSendTime)
                    {
                        currentvar.elapsedtime = 0;
                        if (currentvar.EnabledMode >= 2)
                        {
                            //Get the variable first
                            var reskvp = KVP.ReadVariable(currentvar.Name);
                            if (reskvp != null && reskvp.readOk)
                            {
                                currentvar.Value = reskvp.value;
                                SendVarProperty(currentvar.Name, "Val", currentvar.Value);
                            }
                            else
                            {
                                //SendVarProperty("somethingsomething", "Value", "2");
                                textBox1.AppendText("result null or not ok. \n");
                                KVPReconnect();
                            }

                        }
                    }

                    if (currentvar.EnabledMode == 1 | currentvar.EnabledMode == 3)
                    {

                        //textBox1.AppendText("tickkq:" + currentvar.Name + "\n");
                        //Get the variable first
                        var reskvp = KVP.ReadVariable(currentvar.Name);
                        if (reskvp != null && reskvp.readOk)
                        {
                            currentvar.Value = reskvp.value;
                            // SendVarProperty(currentvar.Name, "Value", currentvar.Value);
                        }
                        else
                        {
                            textBox1.AppendText("result null or not ok. \n");
                            KVPReconnect();
                        }

                        double ival;
                        var result = double.TryParse(currentvar.Value, out ival);
                        if (result)
                        {
                            if (Math.Abs(ival - currentvar.elapsedvalue) >= currentvar.AutoSendValue)
                            {
                                currentvar.elapsedvalue = ival;
                                if (currentvar.Value.Length > 6)
                                {
                                    currentvar.Value = currentvar.Value.Substring(0, 6);
                                }

                                SendVarProperty(currentvar.Name, "Val", currentvar.Value);
                            }
                        }
                        else
                        {
                            textBox1.AppendText("could not parse. \n");
                        }
                    }

                }
            }
            catch(Exception ex)
            {
                textBox1.AppendText(ex.Message);
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            AddAxesVar();
        }


        private string frame_to_string(KvasPos pos)
        {
            string val_string = String.Format("{{X {0:0.##}, Y {1:0.##}, Z {2:0.##}, A {3:0.##}, B {4:0.##}, C {5:0.##}}}", pos.v1, pos.v2, pos.v3, pos.v4, pos.v5, pos.v6);
            return val_string;
        }
        private void AddAxesVar()
        {
            Variables.Add(new RobVar("$AXIS_ACT.A1") { EnabledMode = 3 });
            Variables.Add(new RobVar("$AXIS_ACT.A2") { EnabledMode = 3 });
            Variables.Add(new RobVar("$AXIS_ACT.A3") { EnabledMode = 3 });
            Variables.Add(new RobVar("$AXIS_ACT.A4") { EnabledMode = 3 });
            Variables.Add(new RobVar("$AXIS_ACT.A5") { EnabledMode = 3 });
            Variables.Add(new RobVar("$AXIS_ACT.A6") { EnabledMode = 3 });
            if (ROBOT_NAME == "KR10")
            {
                Variables.Add(new RobVar("$AXIS_ACT.L1") { EnabledMode = 3 });
            }

        }

        private void button2_Click(object sender, EventArgs e)
        {
            if (!Serial.IsOpen)
            {
                Serial.Open();
            }
            Serial.NewLine = "\n";
            Serial.WriteLine("testtopic/vooooogel/vogel2");
            SendVarProperty("$AXIS_ACT.A1", "Value", "3");
        }

        private void KVPReconnect()
        {
            KVP.Disconnect();

            KVP = new KVPInterface();
            KVP.IP = "10.104.117.2";
            KVP.Port = 7000;
            KVP.timeout = 100;
            ConnectKVP();
        }

        private void checkBox1_CheckedChanged(object sender, EventArgs e)
        {
            debugflag = checkBox1.Checked;
        }

        private void numericUpDown1_ValueChanged(object sender, EventArgs e)
        {
            var nval = (int)numericUpDown1.Value;
            if (nval <= 0)
            {
                //Something wrong, got to fix it
                nval = 1;
            }
            timer2.Interval = nval;
            AppendText("Changed update period: " + nval.ToString() + "\n");

        }

        private void checkBox2_CheckedChanged(object sender, EventArgs e)
        {
            this.debug_flag = checkBox2.Checked;
        }

        private void checkBox3_CheckedChanged(object sender, EventArgs e)
        {
            this.debug_heartbeat = checkBox3.Checked;
        }

        private void numericUpDown2_ValueChanged(object sender, EventArgs e)
        {
            try
            {
                Serial.Close();
                Serial.PortName = (String.Format("COM{0}", numericUpDown2.Value));

            }
            catch
            {

            }
        }

        private void button1_Click_1(object sender, EventArgs e)
        {
            KVP.WriteVariable("my_inc", textBox2.Text);
        }
    }

}



