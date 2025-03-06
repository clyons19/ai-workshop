select * from DogTable
left join DogFoodTable on DogTable.FavoriteFoodID = DogFoodTable.ID
where DogFoodTable.Price < 25