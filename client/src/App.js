import './App.css';
import * as React from 'react';
import ColorToggleButton from './components/toggle'
import InputComponent from "./components/inputComponent";
class App extends React.Component{

    state={
        a : 6
    }
    render(){
    return(
        <div className="App">
            <div className="right">
                <div className="inline">
                    <InputComponent value={0} label={"Количество машин"} type={"number"}
                                    onChange={() => console.log(1)}/>
                    <InputComponent value={false} label={"Радиус поиска маршрутов"} variant={"input"}
                                    type={"checkbox"}/>

                </div>
                <InputComponent vallue={0} type={"range"}/>
                <div className="inline">
                    <button>Смоделировать</button>
                    <button>Очистить точки на карте</button>
                </div>
                <text>Количество маршрутов: {this.state.a}</text>
                <br/>
                <ColorToggleButton/>
            </div>
            <div align="center">
                <div class="table">
                    <div class="row">
                        <div class="cell">
                            <canvas id="map" width="500" height="500"/>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    )
  }
}

export default App;
