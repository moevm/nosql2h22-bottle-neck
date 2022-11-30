import * as React from 'react';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import Roads from "./roads";
import Routes from "./routes";

export default function ColorToggleButton({typeRoads, address, minWorkload, maxWorkload, minLenght, maxLenght, minTime, maxTime, filterRoads, filterRoutes, dataRoads, dataRoutes}) {
  const [alignment, setAlignment] = React.useState('Дороги');
  const handleChange = (event, newAlignment) => {
    setAlignment(newAlignment);
  };
  function getIndormation(){
    if(alignment === 'Дороги'){
      return (<Roads data={dataRoads} address={address} typeRoads={typeRoads} minWorkload={minWorkload} maxWorkload={maxWorkload} filter={filterRoads}/>)
    }
    else if(alignment === 'Маршруты'){
      return (<Routes data={dataRoutes} minLRef={minLenght} maxLRef={maxLenght} minTRef={minTime} maxTRef={maxTime} filter={filterRoutes}/>)
    }
  }
  return (
    <div>
      <ToggleButtonGroup
        color="primary"
        value={alignment}
        exclusive
        onChange={handleChange}
        aria-label="Platform"
      >
        <ToggleButton value="Дороги">Дороги</ToggleButton>
        <ToggleButton value="Маршруты">Маршруты</ToggleButton>
      </ToggleButtonGroup>
      {getIndormation()}
    </div>
  );
}