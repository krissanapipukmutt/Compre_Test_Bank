<html>
    <body>
        <?php
            echo "<h2>RESULT </h2>";
            echo "User name is : ".$_GET["name"]."<br>";
            echo $_GET["num_1"]." ".$_GET["operator"]." ".$_GET["num_2"];
            echo "<br><br>";
            $num1 = $_GET["num_1"];
            $num2 = $_GET["num_2"];
            $Operator = $_GET["operator"];
            if($Operator == "+"){
                $result = $num1+$num2;
                echo "Result is : ".$result;
                echo "<br><br>";}
            else if($Operator == "-"){
                $result = $num1-$num2;
                echo "Result is : ".$result;
                echo "<br><br>";}
            else if($Operator == "/"){
                $result = $num1/$num2;
                echo "Result is : ".$result;
                echo "<br><br>";}
            else if($Operator == "*"){
                $result = $num1*$num2;
                echo "Result is : ".$result;
                echo "<br><br>";}
        ?>
    </body>
</html>