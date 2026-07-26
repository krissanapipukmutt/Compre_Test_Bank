<html>
    <body>
        <?php
            echo "<h2> BMI RESULT </h2>";
            echo "Your height is : ".$_GET["height"]." m.";
            echo "<br><br>";
            echo "Your weight is : ".$_GET["weight"]." kg.";
            echo "<br><br>";
            $w = $_GET["weight"];
            $h = $_GET["height"];
            $result = $w/($h*$h);
            echo "Your result is : ".$result;
            echo "<br><br>";
            // < 18 uderweight
            // 18.5-24.9 normal
            // 25-29.9 overweight
            // >30 obesity
            if ($result < 18)
                echo "Uderweight <br> <img src=\"thin.png\" alt=\"thin\" width=100 height=100>";
            else if ($result >= 18.5 and $result <= 24.9)
                echo "Normal <br> <br> <img src=\"healthy.png\" alt=\"healthy\"width=100 height=100>";
            else if ($result > 24.9 and $result <= 29.9)
                echo "Overweight <br> <br> <img src=\"fat.jpg\" alt=\"png\"width=100 height=100>";
            else if ($result > 29.9 )
                echo "Obesity <br> <br> <img src=\"obesity.png\" alt=\"obesity\"width=100 height=100>";
            
        ?>
    </body>
</html>