
Public Class Form1
    Private KVP As New KVPInterface
    Private readvarlist As New List(Of String)

    Private Sub Form1_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        readvarlist.Add("$V_ROBCOR[]")
        readvarlist.Add("$MODEL_NAME[]")
        readvarlist.Add("$OV_PRO")
        readvarlist.Add("$AXIS_ACT")
        readvarlist.Add("$AXIS_ACT.A1")
        readvarlist.Add("$POS_ACT")
        readvarlist.Add("$TIMER[1]")
        readvarlist.Add("$TIMER_STOP[1]")
        readvarlist.Add("$TIMER[1]>0")
        readvarlist.Add("$TORQUE_AXIS_ACT[]")
        readvarlist.Add("$DATE")
        readvarlist.Add("ACOS(0.5)")
        For Each v In readvarlist
            ListBox1.Items.Add(v)
        Next
    End Sub

    'connect to robot
    Private Sub Button4_Click(sender As Object, e As EventArgs) Handles Button4.Click
        'KVP.Connect("ip address", port, timeout_ms)
        If KVP.Connect(TextBox4.Text, 7000, 1000) Then
            Button4.BackColor = Color.Green
        Else
            Button4.BackColor = Color.Red
            MsgBox("Unable to connect to " + TextBox4.Text + ":7000. Configure KLI firewall. Is KUKAVARPROXY.exe running on robot?")
        End If
    End Sub

    Private Sub Form1_Close() Handles MyBase.FormClosing
        KVP.Disconnect()
    End Sub

    'write single variable
    Private Sub Button1_Click(sender As Object, e As EventArgs) Handles Button1.Click
        'KVP.WriteVariable("name","value")
        If KVP.WriteVariable(TextBox2.Text, TextBox3.Text) Then
            Label1.Text = "W-OK"
        Else
            Label1.Text = "W-ERR"
        End If
    End Sub

    'read single variable
    Private Sub Button2_Click(sender As Object, e As EventArgs) Handles Button2.Click
        Dim read_value As New KVPInterface.RobotReadResult

        'KVP.ReadVariable("name")
        read_value = KVP.ReadVariable(TextBox1.Text)

        If read_value.ReadOrWriteOk Then
            Label2.Text = "R-OK"
            RichTextBox1.Text = read_value.ParseAs("string")
        Else
            Label2.Text = "R-ERR"
        End If
    End Sub

    'read all variables in readvarlist
    Private Sub Button3_Click(sender As Object, e As EventArgs) Handles Button3.Click
        ListBox2.Items.Clear()
        Dim stw As New Stopwatch
        
        For Each v In readvarlist
            Dim rval As New KVPInterface.RobotReadResult
            stw.Stop()
            stw.Reset()
            stw.Start()
            rval = KVP.ReadVariable(v)
            stw.Stop()

            Label3.Text = "single variable transaction time: " + stw.ElapsedMilliseconds.ToString() + "ms"

            If Not rval Is Nothing Then
                If rval.ReadOrWriteOk Then
                    ListBox2.Items.Add(rval.ParseAs("string"))
                Else
                    ListBox2.Items.Add("VARIABLE READ ERROR")
                End If
            End If
        Next
    End Sub

End Class
