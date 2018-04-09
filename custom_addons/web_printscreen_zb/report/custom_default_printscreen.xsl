<?xml version = '1.0' encoding="utf-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">
	<xsl:template name="first_page_graphics_corporation">
		<!--logo-->
		<fill color="black"/>
        <stroke color="black"/>
        <setFont name="DejaVu Sans00" size="8"/>
   		<image x="1.3cm" y="19.5cm"><xsl:value-of select="//image"/></image>
        <setFont name="DejaVu Sans00" size="10"/>
        <drawString x="1.3cm" y="18.9cm"><xsl:value-of select="//company"/></drawString>
        <drawRightString  x="28.5cm" y="19.5cm"><xsl:value-of select="//tagline"/></drawRightString>
        <drawRightString  x="28.5cm" y="18.9cm"><xsl:value-of select="//header-date"/></drawRightString>
        <stroke color="#000000"/>
        <lines size="8">1.3cm 19.3cm 28.5cm 19.3cm</lines>
        <lines size="8">1.2cm 2.65cm 28.5cm 2.65cm</lines>
        
        <setFont name="DejaVu Sans00" size="10"/>
        <drawString  x="12.2cm" y="2.3cm">Contact : <xsl:value-of select="//user"/></drawString>
        <drawString  x="15.8cm" y="2.3cm"> - Page: <pageNumber/> </drawString>
	</xsl:template>

   <xsl:template name="first_page_frames">
			<frame id="col1" x1="2.0cm" y1="2.5cm" width="24.7cm" height="16cm"/>
	</xsl:template>

</xsl:stylesheet>