import * as React from 'react';
import InputComponent from "./inputComponent";
export default function Routes() {
    return (<div>
        <div class='inline'>
            <div>
                Длина маршрута в км
                <div className="inline">
                    <InputComponent label={"Min"} type={"Number"}
                                    onChange={() => console.log(1)}/>
                    <InputComponent label={"Max"} type={"Number"}
                                    onChange={() => console.log(1)}/>
                </div>
            </div>
            <div>
                Время в пути в минутах
                <div className="inline">
                    <InputComponent label={"Min"} type={"Number"}
                                    onChange={() => console.log(1)}/>
                    <InputComponent label={"Max"} type={"Number"}
                                    onChange={() => console.log(1)}/>
                </div>
            </div>
        </div>
        <button>Отфильтровать</button>
        <p></p>
        {getTable()}
    </div>)
    function getTable(){
        let table = []
        table.push(<tr>
            <th>№</th>
            <th>Время</th>
            <th>Длина</th>
        </tr>);
        return <table>{table}</table>
    }
}