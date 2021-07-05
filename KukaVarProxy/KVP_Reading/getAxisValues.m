function axisValues = getAxisValues()

data = importdata('moreSampleReadingValues.txt');
newData = split(data);
axisValuesCell = cell(size(newData,1),6);
for i = 1:size(newData,1)
    axisValuesCell(i,:) = [newData(i,3),newData(i,5),newData(i,7),newData(i,9),newData(i,11),newData(i,13)];
    for j = 1:size(axisValuesCell,2)
        axisValuesCell(i,j) = erase(axisValuesCell(i,j),",");
        axisValues(i,j) = str2double(axisValuesCell(i,j));
    end
end

