' Interface for KUKAVARPROXY 2.0
' March 2020
'
' This class initiates a client TCP connection with KUKAVARPROXY.exe on port 7000
' and builds the packets to read/write the variables
' Tested with KUKAVARPROXY 6.1.101 on KRC4 8.3.15
' Tested with KUKAVARPROXY 9.0 on KRC4 8.3
' The socket implementation is synchronous thus it will block the thread until the timeout is elapsed.

Imports System.Net.Sockets
Imports System.Text
Imports System.Threading

Public Class KVPInterface

    <Serializable()>
    Public Class RobotVar
        Public mProgramFeatureName As String
        Public mRobotVarName As String
        Public mRobotVarValue As KVPInterface.RobotReadResult
        Public pendingWriteToRob As Boolean
        Public pendingReadFromRob As Boolean

        Public Overrides Function toString() As String
            Return mRobotVarName
        End Function

        Sub New()
            mRobotVarValue = New RobotReadResult
            mProgramFeatureName = "-"
            mRobotVarName = "-"
            mRobotVarValue.value = "-"
        End Sub
    End Class

    Private mIPAddress As String = ""
    'Private mut As New Mutex()

    Public Class RobotReadResult
        Public value As String = ""
        Public ReadOrWriteOk As Boolean = False

        Public Function ParseAs(type As String) As Object
            If value = "" Then
                Return 0
            End If
            Select Case type.ToUpper
                Case "REAL"
                    Return Double.Parse(value, Globalization.NumberStyles.Float)
                Case "INT"
                    Return Integer.Parse(value, Globalization.NumberStyles.Integer)
                Case "BOOL"
                    Return Boolean.Parse(value)
                Case "CHAR"
                    Return value
                Case Else
                    Return value
            End Select
        End Function
    End Class

    Dim KVPSocket As New TcpClient
    Dim Read_MSG_id As Integer = 0
    Dim Write_MSG_id As Integer = 0

    Public isConnected As Boolean = False

    Public Function Connect(pIPAddress As String, pPort As Integer, timeout As Integer) As Boolean
        mIPAddress = pIPAddress
        Try
            KVPSocket.SendTimeout = timeout
            KVPSocket.ReceiveTimeout = timeout
            'Connect to server using a timeout
            Dim result As IAsyncResult = KVPSocket.BeginConnect(pIPAddress, pPort, Nothing, Nothing)
            result.AsyncWaitHandle.WaitOne(timeout, True)
        Catch ex As Exception
            Return False
        End Try
        isConnected = KVPSocket.Connected
        Return KVPSocket.Connected
    End Function

    Public Sub Disconnect()
        KVPSocket.Close()
        KVPSocket = Nothing
        KVPSocket = New TcpClient
    End Sub

    Public Function ReadVariable(pVarName As String) As RobotReadResult
        'Read Variable request packet structure example:
        '  0  1     2  3        4       5  6   
        ' xx xx  | 00 0A   |   00    | 00 07        | 24 4F 56 5F 50 52 4F
        '        |   10    |    0    |     7        | $  O  V  _  P  R  O
        ' REQ ID | REQ LEN | READ=0  | VAR NAME LEN | VAR NAME CHARS
        '(RANDOM)|

        Dim result As New RobotReadResult

        If Not KVPSocket.Connected Then
            Return result
        End If

        Dim PKT_var_name() As Byte
        Dim enc As New System.Text.ASCIIEncoding()
        PKT_var_name = enc.GetBytes(pVarName)

        Dim PKT_name_length(2) As Byte
        PKT_name_length(0) = (pVarName.Length >> 8) And 255
        PKT_name_length(1) = pVarName.Length And 255

        Dim PKT_mode_is_read As Byte = &H0

        Dim PKT_req_id(2) As Byte
        Read_MSG_id = Read_MSG_id + 1
        If Read_MSG_id > 32768 Then
            Read_MSG_id = 0
        End If
        PKT_req_id(0) = (Read_MSG_id >> 8) And 255
        PKT_req_id(1) = Read_MSG_id And 255

        Dim messageLenght As Short = (3 + PKT_var_name.Length)

        Dim PKT_req_len(2) As Byte
        PKT_req_len(0) = (messageLenght >> 8) And 255
        PKT_req_len(1) = messageLenght And 255

        Dim REQ_packet() As Byte
        ReDim REQ_packet(messageLenght + 4)

        REQ_packet(0) = PKT_req_id(0)
        REQ_packet(1) = PKT_req_id(1)
        REQ_packet(2) = PKT_req_len(0)
        REQ_packet(3) = PKT_req_len(1)
        REQ_packet(4) = PKT_mode_is_read
        REQ_packet(5) = PKT_name_length(0)
        REQ_packet(6) = PKT_name_length(1)
        PKT_var_name.CopyTo(REQ_packet, 7)

        Dim ServerStream As NetworkStream
        Dim RSP_packet(KVPSocket.ReceiveBufferSize) As Byte

        Try
            ServerStream = KVPSocket.GetStream()
            ServerStream.Write(REQ_packet, 0, REQ_packet.Length)
            ServerStream.Flush()
            Dim bytesRead As Integer = ServerStream.Read(RSP_packet, 0, CInt(KVPSocket.ReceiveBufferSize))

            If bytesRead <= 0 Then
                isConnected = False
                'MsgBox("ReadVariable zero bytes recvd")
                result.ReadOrWriteOk = False
                Return result
            End If

        Catch ex As Exception
            isConnected = False
            'MsgBox("ReadVariable ServerStream err")
            result.ReadOrWriteOk = False
            Return result
        End Try

        'Read Variable response packet structure example:
        '  0  1     2  3      4         5  6          
        ' xx xx  | 00 0A   | 00      | 00 06       | 35 35 33 39 39 33 | 00 01 01
        '        |   10    |  0      |     6       | 5  5  3  9  9  3  |  0  1  1
        'SAME AS | RSP LEN | READ=00 | VALUE LEN   | VALUE CHARS       |  TRAILER
        'REQUEST |
        Dim RSP_val_len As Short = ((RSP_packet(5) << 8) And 255) + RSP_packet(6)
        Dim RSP_val_payload As String
        Dim RSP_read_status As Integer = RSP_packet(7 + RSP_val_len + 1)

        result.ReadOrWriteOk = RSP_read_status > 0 And RSP_val_len > 0 And RSP_packet(0) = PKT_req_id(0) And RSP_packet(1) = PKT_req_id(1)
        If result.ReadOrWriteOk Then
            RSP_val_payload = Encoding.ASCII.GetString(RSP_packet, 7, RSP_val_len)
            result.value = RSP_val_payload
        Else
            Read_MSG_id = 0
            result.value = ""
        End If
        Return result
    End Function

    Public Function WriteVariable(pVarName As String, pVarValue As String) As Boolean
        Dim encoding As New System.Text.ASCIIEncoding()
        If Not KVPSocket.Connected Then
            Return False
        End If

        Write_MSG_id = Write_MSG_id + 1
        If Write_MSG_id > 32768 Then
            Write_MSG_id = 0
        End If
        Dim PKT_req_id(2) As Byte
        PKT_req_id(0) = (Write_MSG_id >> 8) And 255
        PKT_req_id(1) = Write_MSG_id And 255

        Dim PKT_mode_is_write As Byte = &H1

        Dim PKT_var_name() As Byte
        PKT_var_name = encoding.GetBytes(pVarName)
        Dim PKT_name_length(2) As Byte
        PKT_name_length(0) = (pVarName.Length >> 8) And 255
        PKT_name_length(1) = pVarName.Length And 255

        Dim PKT_VarValue() As Byte
        PKT_VarValue = encoding.GetBytes(pVarValue)
        Dim PKT_value_len(2) As Byte
        PKT_value_len(0) = (pVarValue.Length >> 8) And 255
        PKT_value_len(1) = pVarValue.Length And 255

        Dim messageLenght As Short = (5 + PKT_var_name.Length + PKT_VarValue.Length)

        Dim PKT_req_len(2) As Byte
        PKT_req_len(0) = (messageLenght >> 8) And 255
        PKT_req_len(1) = messageLenght And 255

        Dim REQ_packet() As Byte
        ReDim REQ_packet(messageLenght + 4)

        'Write Variable request packet structure example:
        '  0  1     2  3      4         5  6           7
        ' xx xx  | 00 0F   | 01       | 00 07        | 24 4F 56 5F 50 52 4F | 00 03   |     31 32 33
        '        |   15    |  1       |     7        | $  O  V  _  P  R  O  |     3   |      1  2  3
        ' REQ ID | REQ LEN | WRITE=1  | VAR NAME LEN | VAR NAME CHARS       | VAL LEN | VAL AS STRING
        ' req len of fields from 3 onwards

        REQ_packet(0) = PKT_req_id(0)
        REQ_packet(1) = PKT_req_id(1)
        REQ_packet(2) = PKT_req_len(0)
        REQ_packet(3) = PKT_req_len(1)
        REQ_packet(4) = PKT_mode_is_write
        REQ_packet(5) = PKT_name_length(0)
        REQ_packet(6) = PKT_name_length(1)
        PKT_var_name.CopyTo(REQ_packet, 7)
        PKT_value_len.CopyTo(REQ_packet, 7 + PKT_var_name.Length)
        PKT_VarValue.CopyTo(REQ_packet, 7 + PKT_var_name.Length + PKT_value_len.Length - 1)

        Dim ServerStream As NetworkStream
        Dim RSP_packet(KVPSocket.ReceiveBufferSize) As Byte

        Try
            ServerStream = KVPSocket.GetStream()
            ServerStream.Write(REQ_packet, 0, REQ_packet.Length)
            Dim bytesRead As Integer = ServerStream.Read(RSP_packet, 0, CInt(KVPSocket.ReceiveBufferSize))

            If bytesRead <= 0 Then
                isConnected = False
                'MsgBox("WriteVariable zero bytes recvd")
                Return False
            End If
        Catch ex As Exception
            isConnected = False
            'MsgBox("WriteVariable ServerStream err")
            Return False
        End Try

        'Write Variable response packet structure example:
        '  0  1     2  3         4      5  6  
        ' xx xx  | 00 0A   |    01   | 00 06       | 35 35 33 39 39 33   | 00  | 01 01
        '        |    10   |     1   |     6       |  5  5  3  9  9  3   |  0  |  1  1
        'SAME AS | RSP LEN | WRITE=1 | VALUE LEN   | WRITTEN VALUE CHARS | PAD | READ status 01 01 = OK
        'REQUEST |

        Dim RSP_val_len As Short = ((RSP_packet(5) << 8) And 255) + RSP_packet(6)
        Dim RSP_val_payload As String

        RSP_val_payload = encoding.GetString(RSP_packet, 7, RSP_val_len)
        Dim RSP_read_status As Integer = RSP_packet(7 + RSP_val_len + 1)

        Return RSP_read_status > 0 And RSP_packet(0) = PKT_req_id(0) And RSP_packet(1) = PKT_req_id(1)
    End Function
End Class
