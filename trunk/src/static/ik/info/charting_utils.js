/*    ik-site: A website for information about inselkampf world 1
#    Copyright (C) 2008  Noah C. Jacobson
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
*/
/*
** Build a time axis that is auto-scaled to the input data.
**
** data - an array of objects with a 'time' member.
**
*/
function buildAxisX(data)
{
	//Find the bounds
	low = data[0].time;
	high = data[0].time;
	for( i=0 ; i<data.length ; i++)
	{
		var obj = data[i];

		//If lower
		if( obj.time < low)
			low = obj.time;

		//If higher
		if( obj.score > high)
			high = obj.time;
	}

	var xA = new dojo.charting.Axis();
	xA.range={upper:high, lower:low};
	xA.origin=0;
	xA.showTicks = false;
	xA.showLabel = true;
	xA.label = "Date";

	//5 tick marks
	xA.labels = []
	var nMarks = 10;
	for( i=0; i<(nMarks-1) ; i++)
	{
		var time_seconds = low + Math.floor( (high-low)*(i/(nMarks-1)) );

		date = new Date(1000*time_seconds);
		label = date.getDate() + "/" + (date.getMonth() + 1);

		xA.labels.push( {label: label, value:time_seconds } );
	}
	//Now put the last on
	date = new Date(1000*high);
	label = date.getDate() + "/" + (date.getMonth() + 1);
	xA.labels.push( {label: label+'', value:high} );

	return xA;
}


/*
** Build a Axis that is auto-scaled to the input data.
**
** data - an array of data points with a member with the name 'property'
** property - the name of the member in the data array that corresponds to the y value.
*/
function buildAxisY(data, property)
{
	//Find the bounds
	low = 0;
	high = data[0][property];
	for( i=0 ; i<data.length ; i++)
	{
		var obj = data[i];

		//If higher
		if( obj[property] > high)
			high = obj[property];
	}

	var yA = new dojo.charting.Axis();
	yA.range={upper: high*1.05, lower:low}; //high*1.05 leaves a little space at the top of the graph
	yA.showLines = true;
	yA.showTicks = true;
	yA.showLabel = true;

	//5 tick marks
	yA.labels = []
	var nMarks = 5;
	for( i=0; i<(nMarks-1) ; i++)
	{
		var tick_value = low + Math.floor( (high-low)*(i/(nMarks-1)) );
		yA.labels.push( {label: tick_value+'', value:tick_value } );
	}
	//Now put the last on
	yA.labels.push( {label: high+'', value:high} );

	return yA;
}