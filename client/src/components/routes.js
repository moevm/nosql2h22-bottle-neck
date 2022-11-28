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
        table.push(
            <table>
                <thead>
                <tr>
                    <th className="text-left">№</th>
                    <th className="text-left">Время</th>
                    <th className="text-left">Длина</th>
                </tr>
                </thead>
            </table>
        );
        table.push(<div className="table-scroll-body">
            <table>
                <tbody>
                <tr>
                    <td>Азу</td>
                    <td>11,9</td>
                    <td>14,2</td>
                </tr>
                <tr>
                    <td>Азу</td>
                    <td>11,9</td>
                    <td>14,2</td>
                </tr>
                <tr>
                    <td>Азу</td>
                    <td>11,9</td>
                    <td>14,2</td>
                </tr>
                <tr>
                    <td>Азу</td>
                    <td>11,9</td>
                    <td>14,2</td>
                </tr><tr>
                    <td>Азу</td>
                    <td>11,9</td>
                    <td>14,2</td>
                </tr>
                <tr>
                    <td>Азу</td>
                    <td>11,9</td>
                    <td>14,2</td>
                </tr>
                <tr>
                    <td>Азу</td>
                    <td>11,9</td>
                    <td>14,2</td>
                </tr>
                </tbody>
            </table>
        </div>)
        return <div className="table-scroll">{table}</div>
    }
}