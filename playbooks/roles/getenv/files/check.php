<?php
//$osversion_res = php_uname('s');
$phpversion_res = PHP_VERSION;
$array_module = get_loaded_extensions();
//print_r($array_module);
if (in_array('bcmath', $array_module)) {
	$bcmath_res = "bcmath库已安装";
} else {
	$bcmath_res = "bcmath库未安装，请先安装gd库";
}
if (in_array('fileinfo', $array_module)) {
	$fileinfo_res = "fileinfo库已安装";
} else {
	$fileinfo_res = "fileinfo库未安装，请先安装fileinfo库";
}
if (in_array('openssl', $array_module)) {
	$openssl_res = "openssl库已安装";
} else {
	$openssl_res = "openssl库未安装，请先安装openssl库";
}
$array_gdinfo = gd_info();
//print_r($gdinfo);
if ($array_gdinfo['FreeType Support']) {
	$gd_freetype_res = "gd库支持freetype.";
} else {
	$gd_freetype_res = "gd库不支持freetype，请安装freetype";
}
?>
<?php
//echo "系统版本: $osversion_res\n";
echo "PHP版本：$phpversion_res\n";
echo "$bcmath_res\n";
echo "$gd_freetype_res\n";
echo "$fileinfo_res\n";
echo "$openssl_res\n";
?>
