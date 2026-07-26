<!DOCTYPE html>
<html>
<body>

<?php
echo "Here is your product list: <br>";
$type = $_GET["txtProductType"];

$servername = "127.0.0.1";
$username = "root";
$password = "";
$dbname = "product_database";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$sql = "SELECT * FROM product WHERE type = '".$type."'";
$result = $conn->query($sql);

echo "<table border=1>";
echo "<tr>";
echo "<td>Product Id</td>";
echo "<td>Product Name</td>";
echo "<td>Unit Price</td>";
echo "<td>Quantity</td>";
echo "</tr>";

while($row = $result->fetch_assoc()) {
    echo "<tr>";
    echo "<td>".$row["id"]."</td>";
    echo "<td>".$row["name"]."</td>";
    echo "<td>".$row["unit_price"]."</td>";
    echo "<td>".$row["quantity"]."</td>";
    echo "</tr>";
}

echo "</table>";
?>

</body>
</html>
