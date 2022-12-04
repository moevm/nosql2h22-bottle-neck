import * as React from 'react';
import InputComponent from "./inputComponent";
export default function Routes({minLRef, maxLRef, minTRef, maxTRef, filter, data}) {
    return (<div>
        <div class='inline'>
            <div>
                Длина маршрута в км
                <div className="inline">
                    <InputComponent label={"Min"} type={"Number"}
                                    onChange={() => console.log(1)} sRef={minLRef}/>
                    <InputComponent label={"Max"} type={"Number"}
                                    onChange={() => console.log(1)} sRef={maxLRef}/>
                </div>
            </div>
            <div>
                Время в пути в минутах
                <div className="inline">
                    <InputComponent label={"Min"} type={"Number"}
                                    onChange={() => console.log(1)} sRef={minTRef}/>
                    <InputComponent label={"Max"} type={"Number"}
                                    onChange={() => console.log(1)} sRef={maxTRef}/>
                </div>
            </div>
        </div>
        <button onClick={filter}>Отфильтровать</button>
        <p></p>
        {getTable()}
    </div>)
    function getTable(){
        let table = []
        if(data != null)
            table.push(<div>Количество маршрутов {data.length}</div>)
        table.push(
            <table>
                <thead>
                <tr>
                    <th className="text-left">№</th>
                    <th className="text-left">Длина</th>
                    <th className="text-left">Время</th>
                </tr>
                </thead>
            </table>
        );
        if(data != null){
            let content = []
            for(let i = 0; i < data.length; i++){
                content.push(<tr>
                    <td>{i + 1}</td>
                    <td>{Math.round(data[i].length*100)/100}</td>
                    <td>{Math.round(data[i].time*100)/100}</td>
                </tr>)
            }
            table.push(<div className="table-scroll-body"><table><tbody>{content}</tbody></table></div>)
        }
        return <div className="table-scroll">{table}</div>
    }
}