<?php
/*
Template Name: Charades
*/
?>

<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">

<head>
  <title>Charades Generator</title>
  <link rel="stylesheet" type="text/css" href="console/style.css" />
</head>

<body>

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
$easy_radio = "checked";
$hard_radio = "";

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
    
    if ($level == "easy") {
        $operator = ">=";
    } else {
        $operator = "<";
        $easy_radio = "";
        $hard_radio = "checked";
    }
    
    $mysqli = new mysqli("localhost","otfopcom","s4c98nOTj8","charades") or die(mysql_error());
    $mysqli->autocommit(FALSE);
    
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
        
        printf("<p>Number of items in this category:  ".count($ids)."</p>");
        $randomno = rand(0, count($ids)-1);
        $randomid = $ids[$randomno];
        
        if ($stmt2 = $mysqli->prepare("SELECT title, person, genre, description FROM ".$table." WHERE id = ?")) { 
            $stmt2->bind_param("i",$randomid);
            $stmt2->execute();
            $stmt2->bind_result($title,$author,$genres,$description);
            $stmt2->store_result();
            while ($stmt2->fetch()) {
                
                printf("<p>Title: ".$title."</p>");
                printf("<p>".$person.": ".$author."</p>");
                printf("<p>Genres: ".$genres."</p>");
                printf("<p>Description: ".$description."</p>");
                
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

<input type="radio" name="type" value="book" <? echo $book_radio ?> >Book<br>
<input type="radio" name="type" value="film" <? echo $film_radio ?> >Film<br><br>
<input type="radio" name="level" value="easy" <? echo $easy_radio ?> >Easy<br>
<input type="radio" name="level" value="hard" <? echo $hard_radio ?> >Hard<br><br>
<input type="submit" value="Go!">
</form>

</body>

</html>