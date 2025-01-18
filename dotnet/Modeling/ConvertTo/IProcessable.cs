using System;
using System.Collections.Generic;
using System.Linq;
using System.Numerics;
using System.Text;
using System.Threading.Tasks;

namespace HEIO.NET.Modeling.ConvertTo
{
    internal interface IProcessable
    {
        public Vector3 AABBMin { get; }
        public Vector3 AABBMax { get; }

        public void Process(bool hedgehogEngine2, bool optimizedVertexData);
    }
}
