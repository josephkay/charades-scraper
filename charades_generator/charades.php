<?php
/*
Template Name: Charades
*/
?>

<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">

<head>
  <title>Charades Generator</title>
  <link rel="stylesheet" type="text/css" href="<?php echo get_template_directory_uri(); ?>/charadesstyle.css" />
</head>

<body>
<div id="wrap">

<h1>Charades Generator</h1>

<?
function sanitise($str,$id) {
	$str = stripslashes($str);
	if ($id == True) {
		$whitelist = "1234567890";
	} else {
		$whitelist = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890’'-_!:?@.";
	}
	for($i=0;$i<strlen($str);$i++) {
		$found = 0;
		for($j=0;$j<strlen($whitelist);$j++) {
			if ($str[$i] == $whitelist[$j]) {
				$found = 1;
				break;
			}
		}
		if ($found == 0) {
			return False;
		}
	}
	$str = addslashes($str);
	return $str;
}

$book_radio = "checked";
$film_radio = "";
$known_radio = "checked";
$obscure_radio = "";

if (isset($_GET['type']) AND isset($_GET['level'])) {
    
    $type = sanitise($_GET['type'],False);
    $level = sanitise($_GET['level'],False);
    
    
    // Change it so that it collects a list of ids and then selects one from there based on a random number from the length of the list.
    
    if ($type == "book") {
        $table = "books";
        $thresh = 100000;
        $statement = "SELECT id FROM books WHERE votes > ?";
        $person = "Author";
    } else {
        $table = "films";
        $thresh = 100;
        $statement = "SELECT id FROM films WHERE votes > ?";
        $book_radio = "";
        $film_radio = "checked";
        $person = "Director";
    }
    
    if ($level == "known") {
        $operator = ">=";
    } else {
        $operator = "<";
        $known_radio = "";
        $obscure_radio = "checked";
    }
    
    $mysqli = new mysqli("localhost","otfopcom","s4c98nOTj8","charades") or die(mysql_error());
    $mysqli->autocommit(FALSE);
    
    if ($stmt = $mysqli->prepare("SET NAMES utf8")) {
        $stmt->execute();
    } else {
        printf("Prepared Statement Error: %s\n", $mysqli->error);
        $mysqli->rollback();
    }
    
    //if ($stmt = $mysqli->prepare($count_statement.$difference."2000")) {
    if ($stmt = $mysqli->prepare("SELECT id FROM ".$table." WHERE votes ".$operator." ?")) {
    //if ($stmt = $mysqli->prepare("SELECT id FROM films WHERE votes < ?")) {
        $stmt->bind_param("i",$thresh);
        $stmt->execute();
        $stmt->bind_result($id);
        $stmt->store_result();
        $ids = array();
        while ($stmt->fetch()) {
            
            array_push($ids, $id);
        }
        
        //printf("<p>Number of items in this category:  ".count($ids)."</p>");
        $randomno = rand(0, count($ids)-1);
        $randomid = $ids[$randomno];
        
        if ($stmt2 = $mysqli->prepare("SELECT title, person, genre, description FROM ".$table." WHERE id = ?")) { 
            $stmt2->bind_param("i",$randomid);
            $stmt2->execute();
            $stmt2->bind_result($title,$author,$genres,$description);
            $stmt2->store_result();
            while ($stmt2->fetch()) {
                
                try {
                    printf("<table id='details'><tr><td class='label'>Title:</td><td>".$title."</td></tr>");
                    printf("<tr><td class='label'>".$person.":</td><td>".$author."</td></tr>");
                    printf("<tr><td class='label'>Genres:</td><td>".$genres."</td></tr>");
                    printf("<tr><td class='label'>Description:</td><td>".$description."</td></tr></table>");
                } catch (Exception $e) {
                    printf("<p>Sorry! Something went wrong... Try again!</p>");
                }
                
                
            }
        }
    } else {
        printf("Prepared Statement Error: %s\n", $mysqli->error);
        $mysqli->rollback();
    }
    
    $mysqli->commit();
    $mysqli->close();
}



?>

<form action="http://www.joseph-kay.com/creations/charades" method="get">

<table id="form">
<tr>
<td>
<input type="radio" name="type" value="book" id="book" <? echo $book_radio ?> ><label for="book">Book</label>
</td>
<td>
<input type="radio" name="level" value="known" id="known" <? echo $known_radio ?> ><label for="known">Well known</label>
</td>
</tr>
<tr>
<td>
<input type="radio" name="type" value="film" id="film" <? echo $film_radio ?> ><label for="film">Film</label>
</td>
<td>
<input type="radio" name="level" value="obscure" id="obscure" <? echo $obscure_radio ?> ><label for="obscure">Obscure</label>
</td>
</tr>
</table>
<table id="submittable">
<tr>
<td>
<input type="submit" value="Go!" id="submit">
</td>
</tr>
</table>

</form>

</div>
</body>

</html>