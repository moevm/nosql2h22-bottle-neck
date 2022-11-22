import * as React from 'react';
import ToggleButton from '@mui/material/ToggleButton';
import ToggleButtonGroup from '@mui/material/ToggleButtonGroup';
import Roads from "./roads";
import Routes from "./routes";

export default function ColorToggleButton() {
  const [alignment, setAlignment] = React.useState('Дороги');
  const handleChange = (event, newAlignment) => {
    setAlignment(newAlignment);
  };
  function getIndormation(){
    if(alignment === 'Дороги'){
      return (<Roads/>)
    }
    else if(alignment === 'Маршруты'){
      return (<Routes/>)
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