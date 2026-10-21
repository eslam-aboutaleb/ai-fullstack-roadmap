input_channels,output_channels,kernel=3,16,3
parameters=output_channels*input_channels*kernel*kernel+output_channels
assert parameters == 448
print(parameters)
