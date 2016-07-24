function CreateTimeZoneOption(id)
{
    var obj = document.getElementById(id);
    obj.options.add(new Option("UTC-12:00", -12))
    obj.options.add(new Option("UTC-11:00", -11))
    obj.options.add(new Option("UTC-10:00", -10))
    obj.options.add(new Option("UTC-09:00", -9))
    obj.options.add(new Option("UTC-08:00", -8))
    obj.options.add(new Option("UTC-07:00", -7))
    obj.options.add(new Option("UTC-06:00", -6))
    obj.options.add(new Option("UTC-05:00", -5))
    obj.options.add(new Option("UTC-04:00", -4))
    obj.options.add(new Option("UTC-03:00", -3))
    obj.options.add(new Option("UTC-02:00", -2))
    obj.options.add(new Option("UTC-01:00", -1))
    obj.options.add(new Option("UTC 00:00", 0))
    obj.options.add(new Option("UTC+01:00", 1))
    obj.options.add(new Option("UTC+02:00", 2))
    obj.options.add(new Option("UTC+03:00", 3))
    obj.options.add(new Option("UTC+04:00", 4))
    obj.options.add(new Option("UTC+05:00", 5))
    obj.options.add(new Option("UTC+06:00", 6))
    obj.options.add(new Option("UTC+07:00", 7))
    obj.options.add(new Option("UTC+08:00", 8))
    obj.options.add(new Option("UTC+09:00", 9))
    obj.options.add(new Option("UTC+10:00", 10))
    obj.options.add(new Option("UTC+11:00", 11))
    obj.options.add(new Option("UTC+12:00", 12))
}

function CreateNationOption(id, list, val)
{
    var obj = $("#"+id);
    for (var i in list)
    {
        var select = "";
        if(val == list[i][1])
            select = "selected";
        var option = "<option value='"+list[i][1]+"' "+select+">"+list[i][0]+"</option>";
        obj.append(option);
    }
}
